import argparse, pandas as pd
from sklearn.model_selection import train_test_split

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_csv", required=True)     # gs://.../data/penguins_clean.csv
    p.add_argument("--out_dir", required=True)       # gs://.../runs/<run-id>/
    a = p.parse_args()

    cols = ["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","species"]
    df = pd.read_csv(a.input_csv)[cols].dropna()
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["species"])
    train.to_csv(f"{a.out_dir}/train.csv", index=False)
    test.to_csv(f"{a.out_dir}/test.csv", index=False)

if __name__ == "__main__":
    main()
