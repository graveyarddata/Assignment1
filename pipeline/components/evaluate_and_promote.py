import argparse, json, pandas as pd, joblib, fsspec, os

def cp(src, dst):
    with fsspec.open(src, "rb") as s, fsspec.open(dst, "wb") as d:
        d.write(s.read())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test_csv", required=True)      # gs://.../runs/<run-id>/test.csv
    p.add_argument("--model_pkl", required=True)     # gs://.../runs/<run-id>/model.pkl
    p.add_argument("--out_dir", required=True)       # gs://.../runs/<run-id>/
    p.add_argument("--model_dir", required=True)     # gs://.../models
    a = p.parse_args()

    df = pd.read_csv(a.test_csv)
    X = df[["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]]
    y = df["species"]

    model = joblib.load(fsspec.open(a.model_pkl, "rb"))
    acc = float((model.predict(X) == y).mean())

    # write metrics for this run
    with fsspec.open(f"{a.out_dir}/metrics.json","w") as f:
        json.dump({"accuracy": acc}, f)

    # simple promotion: always overwrite gs://.../models/model.*
    run_dir = os.path.dirname(a.model_pkl)
    cp(f"{run_dir}/model.pkl",        f"{a.model_dir}/model.pkl")
    cp(f"{run_dir}/model_meta.json",  f"{a.model_dir}/model_meta.json")
    cp(f"{a.out_dir}/metrics.json",   f"{a.model_dir}/metrics.json")
    print("accuracy=", acc, "| promoted to", a.model_dir)

if __name__ == "__main__":
    main()
