# ===== API FILE =====
# Purpose: receive 4 numbers, load model (from GCS in prod), return JSON {"species":"Adelie"}

# importing Flask and other modules
from flask import Flask, request, jsonify
import os, tempfile, joblib, numpy as np

# Flask constructor
app = Flask(__name__)

# Turn this on in Cloud Run to load the model from GCS
USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"
if USE_GCS:
    from google.cloud import storage

# ---- MODEL SETUP TO CONNECT TO STORAGE ----
# Configure these environment variables in Cloud Run; defaults for local testing
MODEL_BUCKET = os.getenv("MODEL_BUCKET", "assignment1group3")
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")   # path inside bucket
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "./model.pkl")      # used for local testing

def load_model():
    """Load model from GCS if USE_GCS=true, else from local file."""
    try:
        if USE_GCS:
            client = storage.Client()
            blob = client.bucket(MODEL_BUCKET).blob(MODEL_PATH)
            with tempfile.TemporaryDirectory() as td:
                tmp_path = os.path.join(td, "model.pkl")
                blob.download_to_filename(tmp_path)
                return joblib.load(tmp_path)
        else:
            return joblib.load(LOCAL_MODEL)
    except Exception as e:
        # Log in real life; for now raise to fail fast at startup
        raise RuntimeError(f"Failed to load model: {e}")

# Load the model once at startup
model = load_model()

# ---- API ROUTE ----
# A decorator used to tell the application which URL is associated with the function
@app.route('/what_penguin_are_you', methods=["GET", "POST"])
def check_penguin():
    # GET: describe how to use this endpoint (API doesn't serve HTML)
    if request.method == "GET":
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
    data = request.get_json(silent=True)
    try:
        bl = float(data["bill_length_mm"])
        bd = float(data["bill_depth_mm"])
        fl = float(data["flipper_length_mm"])
        bm = float(data["body_mass_g"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Invalid or missing fields"), 400

    X = np.array([[bl, bd, fl, bm]], dtype=float)
    try:
        pred = model.predict(X)[0] # expect label: Adelie/Chinstrap/Gentoo
    except Exception as e:
        return jsonify(error=f"Prediction failed: {e}"), 500
    return jsonify(species=str(pred)), 200


# -------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "5000")))
