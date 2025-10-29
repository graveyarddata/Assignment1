import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import google.cloud.aiplatform as aip


def run_pipeline_job(name, pipeline_def, pipeline_root, parameter_dict):
  """This runs the pipeline, similar to last part of pipeline"""
    f = open(parameter_dict)
    data = json.load(f)
    print(data)
    logging.info(data)
    job = aip.PipelineJob(
        display_name=name,
		enable_caching=False,
        template_path=pipeline_def,
        pipeline_root=pipeline_root,
        parameter_values=data)
    job.run()

def parse_command_line_arguments()
