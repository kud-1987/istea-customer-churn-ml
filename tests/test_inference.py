import numpy as np

from app.inference import predict_churn, risk_level
from app.schemas import PredictionRequest
from tests.test_api import VALID_PAYLOAD


class ReverseClassModel:
    classes_ = np.array([1, 0])

    def predict(self, features):
        return np.array([1])

    def predict_proba(self, features):
        return np.array([[0.82, 0.18]])


def test_positive_probability_uses_class_index():
    result = predict_churn(ReverseClassModel(), PredictionRequest(**VALID_PAYLOAD))
    assert result["probability"] == 0.82
    assert result["risk_level"] == "HIGH"


def test_risk_thresholds():
    assert risk_level(0.39) == "LOW"
    assert risk_level(0.4) == "MEDIUM"
    assert risk_level(0.69) == "MEDIUM"
    assert risk_level(0.7) == "HIGH"
