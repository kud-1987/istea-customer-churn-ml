import json
import os
from pathlib import Path

import joblib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "models" / "candidate.joblib"
SELECTION_PATH = ROOT / "reports" / "selection.json"


def get_model_version() -> str:
    configured = os.getenv("MODEL_VERSION")
    if configured:
        return configured
    if SELECTION_PATH.exists():
        selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        return str(selection.get("registered_model_version", "unknown"))
    return "unknown"


def load_model():
    model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")
    model = joblib.load(model_path)
    for method in ("predict", "predict_proba"):
        if not hasattr(model, method):
            raise TypeError(f"Loaded artifact does not implement {method}")
    return model
