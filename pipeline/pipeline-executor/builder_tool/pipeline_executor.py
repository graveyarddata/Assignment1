# Assignment1/pipeline/pipeline-executor/builder_tool/pipeline_executor.py
import argparse
import json
import logging
import os
import sys
from pathlib import Path

from google.cloud import aiplatform as aip


def run_pipeline_job(
    name: str,
    pipeline_def: str,
    pipeline_root: str,
    parameter_dict: str,
    project: str,
    location: str,
    experiment: str | None = None,
    enable_caching: bool = False,
    service_account: str | None = None,
):
    # Init AIP (project + regio zijn cruciaal)
    aip.init(project=project, location=location)

    # Lees parameters (lokaal pad in Cloud Build is /workspace/…)
    params_path = Path(parameter_dict)
    if not params_path.exists():
        raise FileNotFoundError(f"Parameter file not found: {params_path}")

    with params_path.open("r", encoding="utf-8") as f:
        params = json.load(f)

    logging.info("Pipeline parameters: %s", params)

    # Maak en run de job
    job = aip.PipelineJob(
        display_name=name,
        template_path=pipeline_def,  
        pipeline_root=pipeline_root,  
        parameter_values=params,
        enable_caching=enable_caching,
        location=location,            
        project=project,
    )

    logging.info("Submitting PipelineJob …")
    job.run(sync=True)  # wacht tot start; logs verschijnen in Vertex

    logging.info("Job submitted. Resource name: %s", job.resource_name)
    return job.resource_name


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Pipeline display name")
    parser.add_argument("--pipeline_def", required=True,
                        help="Path to compiled pipeline YAML (gs:// or local)")
    parser.add_argument("--pipeline_root", required=True,
                        help="GCS path for pipeline root (gs://...)")
    parser.add_argument("--parameter_dict", required=True,
                        help="Local JSON file with parameter key/values")
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT"),
                        help="GCP project id (defaults to env GOOGLE_CLOUD_PROJECT)")
    parser.add_argument("--location", default=os.getenv("AIP_LOCATION", "us-central1"),
                        help="Vertex AI region (defaults to env AIP_LOCATION or us-central1)")
    parser.add_argument("--experiment", default=None,
                        help="Optional Vertex AI experiment name")
    parser.add_argument("--enable_caching", action="store_true",
                        help="Enable Vertex pipeline caching")
    parser.add_argument("--service_account", default=None,
                        help="Optional service account email to execute the job")
    args = parser.parse_args()

    if not args.project:
        parser.error("--project is required (or set env GOOGLE_CLOUD_PROJECT)")

    return args


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    args = parse_command_line_arguments()

    run_pipeline_job(
        name=args.name,
        pipeline_def=args.pipeline_def,
        pipeline_root=args.pipeline_root,
        parameter_dict=args.parameter_dict,
        project=args.project,
        location=args.location,
        experiment=args.experiment,
        enable_caching=args.enable_caching,
        service_account=args.service_account,
    )


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    run_pipeline_job(**parse_command_line_arguments())
