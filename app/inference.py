import os

import pandas as pd

from app.schemas import PredictionRequest


LOW_RISK_THRESHOLD = float(os.getenv("LOW_RISK_THRESHOLD", "0.4"))
HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.7"))


def request_to_frame(payload: PredictionRequest, feature_order) -> pd.DataFrame:
    row = payload.model_dump()
    return pd.DataFrame([row], columns=list(feature_order))


def risk_level(probability: float) -> str:
    if probability < LOW_RISK_THRESHOLD:
        return "low"
    if probability < HIGH_RISK_THRESHOLD:
        return "medium"
    return "high"


def predict_churn(model, payload: PredictionRequest) -> dict:
    feature_order = getattr(model, "feature_names_in_", payload.model_dump().keys())
    features = request_to_frame(payload, feature_order)
    prediction = int(model.predict(features)[0])

    classes = list(model.classes_)
    try:
        positive_class_index = classes.index(1)
    except ValueError as exc:
        raise ValueError("The model does not contain churn class 1") from exc
    probability = float(model.predict_proba(features)[0][positive_class_index])

    return {
        "prediction": prediction,
        "churn": "Yes" if prediction == 1 else "No",
        "probability": probability,
        "risk_level": risk_level(probability),
    }
