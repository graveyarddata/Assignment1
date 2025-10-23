# train_and_eval.py
import os, json, pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA_CSV = "data/penguins_clean.csv"   # you already uploaded this
OUT_DIR  = "runs"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(DATA_CSV)
    cols = ["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","species"]
    df = df[cols].dropna()

    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["species"])
    Xtr, ytr = train[cols[:-1]], train["species"]
    Xte, yte = test[cols[:-1]],  test["species"]

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=500, multi_class="ovr", random_state=42))
    ])
    pipe.fit(Xtr, ytr)

    acc = float((pipe.predict(Xte) == yte).mean())

    # save artifacts
    joblib.dump(pipe, os.path.join(OUT_DIR, "model.pkl"))
    with open(os.path.join(OUT_DIR, "model_meta.json"), "w") as f:
        json.dump({"classes": sorted(ytr.unique())}, f)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w") as f:
        json.dump({"accuracy": acc}, f)

    print(f"Done. Accuracy={acc:.3f}")
    print(f"Artifacts in ./{OUT_DIR}: model.pkl, model_meta.json, metrics.json")

if __name__ == "__main__":
    main()
