from flask import Flask, request, jsonify
from flask_cors import CORS
import mlflow
import mlflow.pyfunc
import pandas as pd
import numpy as np
import os
import logging

# Prometheus imports
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# --- Configuration ---------------------------------------------------------

# Where MLflow will look for your runs & artifacts
MLFLOW_RUNS_DIR = "/opt/airflow/mlruns"
mlflow.set_tracking_uri(f"file:{MLFLOW_RUNS_DIR}")

# The exact path to your run’s “model” artifact
RUN_ID   = "503374349448629270"
ART_ID   = "4c3d470e49904131ba49bd94d9fd43d0"
MODEL_REL_PATH = f"{RUN_ID}/{ART_ID}/artifacts/model"
MODEL_PATH     = os.path.join(MLFLOW_RUNS_DIR, MODEL_REL_PATH)

# Feature names
FEATURE_COLUMNS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

# --- App & Logging ---------------------------------------------------------

app = Flask(__name__)
CORS(app)

# expose /metrics for Prometheus
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("backend")

# prometheus counter
PREDICTION_COUNTER = Counter(
    "fraud_preds_total",
    "Total number of fraud detection predictions made"
)

# --- Load Model ------------------------------------------------------------

model = None
try:
    log.info(f"Loading model from {MODEL_PATH}")
    model = mlflow.pyfunc.load_model(MODEL_PATH)
    log.info("Model loaded successfully")
except Exception as e:
    log.exception(f" Failed to load model: {e}")

# --- Routes ---------------------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        log.error("Model not loaded, refusing to predict")
        return jsonify({"error": "Model not loaded"}), 500

    PREDICTION_COUNTER.inc()
    try:
        payload = request.get_json(force=True)
        log.debug(f"Request payload: {payload}")

        # build a single-row DataFrame AS FLOATS to satisfy MLflow schema
        features = pd.DataFrame(
            [payload["features"]],
            columns=FEATURE_COLUMNS,
            dtype=float
        )
        log.debug(f"Features df (dtypes):\n{features.dtypes}")

        raw_scores = model.predict(features)  # IsolationForest: -1/1
        prediction = int((raw_scores == -1)[0])
        log.info(f"Prediction computed: {prediction}")

        return jsonify({"prediction": prediction})
    except Exception as e:
        log.exception("Error during prediction")
        return jsonify({"error": str(e)}), 400

@app.route("/health", methods=["GET"])
def health():
    status = "healthy" if model else "unhealthy"
    return jsonify({"status": status})

# --------------------------------------------------------------------------

if __name__ == "__main__":
    # Turn on Flask’s own logger (so you see INFO/debug lines on console)
    app.logger.setLevel(logging.INFO)
    app.run(host="0.0.0.0", port=5001, debug=True)
