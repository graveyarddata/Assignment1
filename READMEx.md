# Assignment 1 — Penguin Species Classifier (End-to-End MLOps on GCP)

An end-to-end machine learning project that trains a logistic-regression classifier on the
Palmer Penguins dataset and serves predictions through a containerised web app on Google
Cloud Platform. The pipeline is built with Vertex AI, automated with
Cloud Build, and the API + UI are deployed to Cloud Run.

The underlying model is adapted from this Kaggle notebook:
<https://www.kaggle.com/code/paulgreber/logistic-regression-with-palmer-s-penguins>

---

## What it does

Given four numeric measurements of a penguin —

- `bill_length_mm`
- `bill_depth_mm`
- `flipper_length_mm`
- `body_mass_g`

— the app predicts the species: **Adelie**, **Chinstrap**, or **Gentoo**.

---

## Architecture

```
                   ┌────────────────────────────────────────────┐
                   │                Cloud Build                 │
                   │  (builds executor image, runs pipeline)    │
                   └──────────────────┬─────────────────────────┘
                                      │
                                      ▼
       ┌──────────────────────────────────────────────────────────┐
       │              Vertex AI Pipeline (Kubeflow)               │
       │  preprocess  ──►  train_lr  ──►  evaluate_and_promote    │
       └──────────────────────────────────────────────────────────┘
                                      │
                            writes model.pkl
                                      ▼
                ┌────────────────────────────────────────┐
                │   GCS bucket: gs://assignment1group3   │
                │   /data, /runs, /models                │
                └─────────────────┬──────────────────────┘
                                  │ loads model
                                  ▼
   ┌─────────────────────────┐        ┌─────────────────────────┐
   │  Cloud Run — UI (Flask) │ ─────► │  Cloud Run — API (Flask)│
   │  HTML form + result     │  POST  │  /what_penguin_are_you  │
   └─────────────────────────┘        └─────────────────────────┘
                  ▲
                  │ browser
                User
```

---

## Repository layout

```
.
├── README.md
├── requirements.txt              # top-level Python deps for local exploration
├── cloudbuild.json               # Cloud Build pipeline (builds + runs the Vertex pipeline)
├── DE_A1.json                    # additional config
│
├── data/
│   ├── penguins_clean.csv        # cleaned Palmer Penguins dataset
│   └── parameters.json           # pipeline parameters (project, GCS paths, ...)
│
├── pipeline/
│   ├── penguinspipeline.ipynb    # notebook used to author/compile the pipeline
│   ├── penguins_pipeline.yaml    # compiled Kubeflow pipeline spec
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── components/
│   │   ├── preprocess_penguins.py
│   │   ├── train_lr.py
│   │   └── evaluate_and_promote.py
│   ├── parameters/parameters.json
│   ├── simple model test/        # notebook + pickled model for sanity-checking
│   └── pipeline-executor/
│       ├── pipeline_executor_tool_cloudbuild.json
│       └── builder_tool/         # container that submits the Vertex AI PipelineJob
│
└── serving/
    ├── api/                      # Flask prediction API (Cloud Run service)
    │   ├── penguin_app_api.py
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── run_api.sh
    └── ui/                       # Flask UI that calls the API (Cloud Run service)
        ├── penguin_app_ui.py
        ├── html form and response pages/
        ├── static/               # penguin images
        ├── Dockerfile
        ├── requirements.txt
        └── run_ui.sh
```

---

## Pipeline components

| Step | Script | What it does |
|------|--------|--------------|
| Preprocess | `pipeline/components/preprocess_penguins.py` | Loads the cleaned CSV, drops NAs, stratified 80/20 split, writes `train.csv` / `test.csv` to GCS. |
| Train | `pipeline/components/train_lr.py` | `StandardScaler` + `LogisticRegression` pipeline, dumps `model.pkl` + `model_meta.json`. |
| Evaluate & promote | `pipeline/components/evaluate_and_promote.py` | Scores on the test set, writes `metrics.json`, and copies the model artefacts to `gs://.../models/`. |

The pipeline is compiled to `pipeline/penguins_pipeline.yaml` and submitted to Vertex AI by
the executor container in `pipeline/pipeline-executor/builder_tool/`.

---

## Serving

- **API** (`serving/api/penguin_app_api.py`) — Flask + gunicorn. On start it downloads
  `gs://$MODEL_BUCKET/$MODEL_BLOB` and serves `POST /what_penguin_are_you` with a JSON body:
  ```json
  { "bill_length_mm": 39.1, "bill_depth_mm": 18.7, "flipper_length_mm": 181, "body_mass_g": 3750 }
  ```
  Response: `{ "species": "Adelie" }`.

- **UI** (`serving/ui/penguin_app_ui.py`) — Flask app that renders an HTML form, POSTs to the
  API URL configured by the `PREDICTOR_API` env var, and shows the predicted species with a
  matching penguin image.

---

## Running locally

Requires Python 3.11+ and (for the API) credentials with read access to the model bucket.

```bash
# 1. API
cd serving/api
pip install -r requirements.txt
export MODEL_BUCKET=assignment1group3
export MODEL_BLOB=models/model.pkl
./run_api.sh                           # serves on http://localhost:8080

# 2. UI (in a second terminal)
cd serving/ui
pip install -r requirements.txt
export PREDICTOR_API=http://localhost:8080
./run_ui.sh                            # open http://localhost:8080/what_penguin_are_you
```

Smoke-test the API directly:

```bash
curl -X POST http://localhost:8080/what_penguin_are_you \
  -H "Content-Type: application/json" \
  -d '{"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750}'
```

---

## Running on GCP

1. Create a GCS bucket and an Artifact Registry repo (default name in `cloudbuild.json`: `mlrepo`).
2. Upload `data/penguins_clean.csv` and `data/parameters.json` to the bucket.
3. Trigger the training pipeline:
   ```bash
   gcloud builds submit --config=cloudbuild.json .
   ```
   This builds the executor image, downloads the parameters from GCS, and submits a Vertex AI
   PipelineJob that trains and promotes `model.pkl` to `gs://<bucket>/models/`.
4. Build & deploy the API and UI to Cloud Run (one service each):
   ```bash
   gcloud run deploy prediction-api --source serving/api --region us-central1
   gcloud run deploy prediction-ui  --source serving/ui  --region us-central1 \
     --set-env-vars PREDICTOR_API=https://<your-api-url>
   ```

---

## Tech stack

Python · scikit-learn · pandas · Flask · gunicorn · Kubeflow Pipelines (KFP) ·
Vertex AI · Cloud Build · Cloud Run · Artifact Registry · Google Cloud Storage · Docker
