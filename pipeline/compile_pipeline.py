import os
from kfp import dsl
from kfp.dsl import component

PROJECT = "assignment1-476007"
REGION  = "us-central1"
BUCKET  = "assignment1group3"                   
IMAGE   = f"{REGION}-docker.pkg.dev/{PROJECT}/mlrepo/penguins-components:latest"
PIPELINE_ROOT = f"gs://{BUCKET}/runs"

@dsl.component(base_image=IMAGE)
def preprocess_op(input_csv: str, out_dir: str):
    import subprocess
    subprocess.check_call([
        "python", "components/preprocess_penguins.py",
        "--input_csv", input_csv, "--out_dir", out_dir
    ])

@dsl.component(base_image=IMAGE)
def train_op(train_csv: str, out_dir: str):
    import subprocess
    subprocess.check_call([
        "python", "components/train_lr.py",
        "--train_csv", train_csv, "--out_dir", out_dir
    ])

@dsl.component(base_image=IMAGE)
def evaluate_and_promote_op(test_csv: str, model_pkl: str, out_dir: str, model_dir: str):
    import subprocess
    subprocess.check_call([
        "python", "components/evaluate_and_promote.py",
        "--test_csv", test_csv, "--model_pkl", model_pkl,
        "--out_dir", out_dir, "--model_dir", model_dir
    ])

@dsl.pipeline(name="penguins-pipeline")
def penguins_pipeline(run_id: str = "manual-run"):
    run_dir = f"gs://{BUCKET}/runs/{run_id}"
    data    = f"gs://{BUCKET}/data/penguins_clean.csv"
    model_d = f"gs://{BUCKET}/models"

    prep = preprocess_op(input_csv=data, out_dir=run_dir)
    trn  = train_op(train_csv=f"{run_dir}/train.csv", out_dir=run_dir).after(prep)
    evaluate_and_promote_op(
        test_csv=f"{run_dir}/test.csv",
        model_pkl=f"{run_dir}/model.pkl",
        out_dir=run_dir,
        model_dir=model_d
    ).after(trn)

if __name__ == "__main__":
    from kfp import compiler
    compiler.Compiler().compile(
        pipeline_func=penguins_pipeline,
        package_path="pipeline_spec.yaml",
        type_check=False
    )
    print("Wrote pipeline_spec.yaml")
