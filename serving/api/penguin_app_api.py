# ===== API FILE =====
# Purpose: receive 4 numbers, load model (from GCS in prod), return JSON {"species":"Adelie"}

# importing Flask and other modules
from flask import Flask, request, jsonify
import os, tempfile, joblib, numpy as np

# Flask constructor
app = Flask(__name__)

# ---- MODEL SETUP (GCS only) ----
from google.cloud import storage
import os, tempfile, joblib

# Fail fast if these aren't set
MODEL_BUCKET = os.environ["MODEL_BUCKET", "assignment1group3"]
MODEL_BLOB   = os.environ.get("MODEL_BLOB", "models/model.pkl")

def load_model():
    """Load model from GCS. Raise if missing/failed."""
    try:
        client = storage.Client()
        bucket = client.bucket(MODEL_BUCKET)
        blob = bucket.blob(MODEL_BLOB)

        # Explicit existence check gives clearer error
        if not blob.exists(client):
            raise FileNotFoundError(f"gs://{MODEL_BUCKET}/{MODEL_BLOB} not found")

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
            blob.download_to_filename(tmp.name)
            tmp_path = tmp.name

        return joblib.load(tmp_path)

    except Exception as e:
        # No local fallback — fail fast
        raise RuntimeError(f"Failed to load model from GCS: {e}")

# Load the model once at startup (will raise on failure)
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
    data = request.get_json()
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
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "8080")))
