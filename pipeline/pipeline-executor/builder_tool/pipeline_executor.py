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
    enable_caching: bool = True,  # <- default so we don't need a CLI flag
):
    # Init Vertex AI
    aip.init(project=project, location=location)

    # Read local params file (downloaded to /workspace/... in Cloud Build)
    params_path = Path(parameter_dict)
    if not params_path.exists():
        raise FileNotFoundError(f"Parameter file not found: {params_path}")

    with params_path.open("r", encoding="utf-8") as f:
        params = json.load(f)

    logging.info("Pipeline parameters: %s", params)

    # Create & run the job
    job = aip.PipelineJob(
        display_name=name,
        template_path=pipeline_def,   # e.g. /workspace/pipeline/penguins_pipeline.yaml
        pipeline_root=pipeline_root,  # e.g. gs://assignment1group3/runs
        parameter_values=params,
        enable_caching=enable_caching,
        location=location,
        project=project,
    )

    logging.info("Submitting PipelineJob …")
    job.run(sync=True)  # wait for submission; detailed logs in Vertex AI

    logging.info("Job submitted. Resource name: %s", job.resource_name)
    return job.resource_name

def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True, help="Pipeline display name")
    parser.add_argument("--pipeline_def", type=str, required=True,
                        help="Path to compiled pipeline spec (YAML/JSON)")
    parser.add_argument("--pipeline_root", type=str, required=True,
                        help="GCS path for pipeline root (gs://...)")
    parser.add_argument("--parameter_dict", type=str, required=True,
                        help="Local JSON file with parameter key/values")
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT"),
                        help="GCP project id (defaults to env GOOGLE_CLOUD_PROJECT)")
    parser.add_argument("--location", type=str, required=True,
                        help="Vertex AI region, e.g. us-central1")
    return parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    args = parse_command_line_arguments()
    # Namespace -> dict for **kwargs
    run_pipeline_job(**vars(args))
