import numpy as np
import pytest
from pydantic import ValidationError
from starlette.requests import Request

from app.main import app, health, predict
from app.schemas import PredictionRequest


VALID_PAYLOAD = {
    "gender": "Female", "SeniorCitizen": 0, "Partner": "Yes",
    "Dependents": "No", "tenure": 1, "PhoneService": "No",
    "MultipleLines": "No phone service", "InternetService": "DSL",
    "OnlineSecurity": "No", "OnlineBackup": "Yes",
    "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "No",
    "StreamingMovies": "No", "Contract": "Month-to-month",
    "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
    "MonthlyCharges": 29.85, "TotalCharges": 29.85,
}


@pytest.fixture(scope="module")
def api_request():
    class ApiModel:
        classes_ = np.array([0, 1])
        feature_names_in_ = np.array(list(VALID_PAYLOAD))

        def predict(self, features):
            return np.array([1])

        def predict_proba(self, features):
            return np.array([[0.28, 0.72]])

    app.state.model = ApiModel()
    app.state.model_version = "1"
    return Request({"type": "http", "app": app})


def test_health_reports_loaded_model(api_request):
    response = health(api_request)
    assert response.model_loaded is True
    assert response.status == "ok"


def test_predict_returns_contract(api_request):
    payload = PredictionRequest(**VALID_PAYLOAD)
    body = predict(payload, api_request)
    assert body.prediction in ["NO_CHURN", "CHURN"]
    assert 0 <= body.probability <= 1
    assert body.risk_level in ["LOW", "MEDIUM", "HIGH"]
    assert body.model_version == "1"
    assert body.request_id


def test_schema_rejects_missing_field():
    invalid = VALID_PAYLOAD.copy()
    invalid.pop("Contract")
    with pytest.raises(ValidationError):
        PredictionRequest(**invalid)


def test_schema_rejects_unknown_category():
    invalid = {**VALID_PAYLOAD, "InternetService": "Satellite"}
    with pytest.raises(ValidationError):
        PredictionRequest(**invalid)


def test_openapi_documentation_is_available():
    schema = app.openapi()
    assert "/predict" in schema["paths"]
    assert schema["paths"]["/predict"]["post"]["responses"]["422"]
