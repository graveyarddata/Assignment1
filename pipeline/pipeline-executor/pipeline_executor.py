#!/usr/bin/env python3
"""
pipeline_executor.py
------------------------------------------
Runs a Vertex AI PipelineJob from a compiled KFP pipeline spec (YAML/JSON)
and an optional parameters.json stored locally or on GCS.

Usage examples:
  python pipeline_executor.py \
    --pipeline_spec_path pipelines/penguins/pipeline.yaml \
    --project assignment1-476007 \
    --region europe-west4 \
    --parameters_uri gs://assignment1group3/data/parameters.json \
    --pipeline_root gs://assignment1group3/runs \
    --display_name penguins-ct-manual

  # Without parameters file (if your pipeline has no params or defaults):
  python pipeline_executor.py \
    --pipeline_spec_path pipelines/penguins/pipeline.yaml \
    --project assignment1-476007 \
    --region europe-west4
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from google.cloud import aiplatform as aip


def _read_params(parameters_uri: Optional[str]) -> Optional[Dict[str, Any]]:
    """Reads parameters from local path or GCS if provided, else returns None."""
    if not parameters_uri:
        return None
    if parameters_uri.startswith("gs://"):
        import gcsfs  # lazy import to keep deps minimal when not needed
        fs = gcsfs.GCSFileSystem()
        with fs.open(parameters_uri, "r") as f:
            return json.load(f)
    # local path
    with open(parameters_uri, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Execute a Vertex AI PipelineJob.")
    parser.add_argument("--pipeline_spec_path", required=True, type=str,
                        help="Path to compiled KFP pipeline spec (YAML or JSON).")
    parser.add_argument("--project", required=True, type=str,
                        help="GCP Project ID.")
    parser.add_argument("--region", required=True, type=str,
                        help="Vertex AI region (e.g., europe-west4).")
    parser.add_argument("--parameters_uri", required=False, type=str, default=None,
                        help="Path to parameters.json (local path or gs://...).")
    parser.add_argument("--pipeline_root", required=False, type=str, default=None,
                        help="Optional gs:// path for pipeline_root (overrides default).")
    parser.add_argument("--display_name", required=False, type=str, default=None,
                        help="Optional display name for the run.")
    parser.add_argument("--sync", action="store_true",
                        help="Block until the job completes (default: run async).")
    parser.add_argument("--enable_caching", action="store_true",
                        help="Enable KFP caching (default: disabled).")

    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    # Init Vertex AI client
    aip.init(project=args.project, location=args.region)

    # Load parameters.json (optional)
    params = _read_params(args.parameters_uri)
    if params is not None:
        logging.info("Loaded parameters:\n%s", json.dumps(params, indent=2, sort_keys=True))
    else:
        logging.info("No parameters file provided; continuing without parameter_values.")

    # Auto display name if not provided
    display_name = args.display_name or f"pipeline-run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # Create and run the PipelineJob
    job = aip.PipelineJob(
        display_name=display_name,
        template_path=args.pipeline_spec_path,
        pipeline_root=args.pipeline_root,         # may be None; Vertex will still run (but best practice is to set it)
        parameter_values=params,                  # may be None
        enable_caching=args.enable_caching,
    )

    logging.info("Submitting PipelineJob: %s", display_name)
    job.run(sync=bool(args.sync))
    logging.info("Submitted. Resource: %s", getattr(job, "resource_name", "<unknown>"))
    if args.sync:
        logging.info("Job finished with state: %s", getattr(job._gca_resource, "state", "<unknown>"))
    else:
        logging.info("Running asynchronously; check status in Vertex AI → Pipelines UI.")


if __name__ == "__main__":
    main()
