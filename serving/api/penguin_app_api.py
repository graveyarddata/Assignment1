# ===== API FILE =====
# Purpose: receive 4 numbers, load model (from GCS in prod), return JSON {"species":"Adelie"}

# importing Flask and other modules
from flask import Flask, request, jsonify
import os, tempfile, joblib, numpy as np

# Flask constructor
app = Flask(__name__)

# ---- MODEL SETUP (GCS only) ----
from google.cloud import storage
import joblib, os

MODEL_BUCKET = os.getenv("MODEL_BUCKET", "assignment1group3")
MODEL_BLOB = os.getenv("MODEL_BLOB", "models/model.pkl")

def load_model():
    client = storage.Client()
    bucket = client.bucket(MODEL_BUCKET)
    blob = bucket.blob(MODEL_BLOB)
    blob.download_to_filename("model.pkl")  # save directly to local file
    return joblib.load("model.pkl")

model = load_model()

# ---- API ROUTE ----
# A decorator used to tell the application which URL is associated with the function
@app.route('/what_penguin_are_you', methods=['GET', 'POST'])
def check_penguin():
    # GET: simple “how to use” doc
    if request.method == 'GET':
        return jsonify({
            "endpoint": "/what_penguin_are_you",
            "use": "POST JSON with four fields to get a species prediction",
            "expected_json": {
                "bill_length_mm": 39.1,
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750
            },
            "returns": {"species": "Adelie | Chinstrap | Gentoo"}
        }), 200

    # POST: do the actual prediction
    data = request.get_json()
    bl = float(data["bill_length_mm"])
    bd = float(data["bill_depth_mm"])
    fl = float(data["flipper_length_mm"])
    bm = float(data["body_mass_g"])

    X = np.array([[bl, bd, fl, bm]])
    raw = int(model.predict(X)[0])  # 0/1/2

    species_map = {0: "Adelie", 1: "Chinstrap", 2: "Gentoo"}
    label = species_map[raw]
    return jsonify(species=label), 200

# -------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "8080")))
