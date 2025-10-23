import argparse, json, pandas as pd, joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train_csv", required=True)     # gs://.../runs/<run-id>/train.csv
    p.add_argument("--out_dir", required=True)       # gs://.../runs/<run-id>/
    a = p.parse_args()

    df = pd.read_csv(a.train_csv)
    X = df[["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]]
    y = df["species"]

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=500, multi_class="ovr", random_state=42))
    ]).fit(X, y)

    joblib.dump(pipe, f"{a.out_dir}/model.pkl")
    with open(f"{a.out_dir}/model_meta.json","w") as f:
        json.dump({"classes": sorted(y.unique())}, f)

if __name__ == "__main__":
    main()
