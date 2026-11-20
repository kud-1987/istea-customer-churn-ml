import numpy as np
import pytest
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

import app.main as main_module


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


class ApiModel:
    classes_ = np.array([0, 1])
    feature_names_in_ = np.array(list(VALID_PAYLOAD))

    def predict(self, features):
        return np.array([1])

    def predict_proba(self, features):
        return np.array([[0.28, 0.72]])


pytestmark = pytest.mark.anyio


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@asynccontextmanager
async def api_client(monkeypatch):
    monkeypatch.setattr(main_module, "load_model", lambda: ApiModel())
    monkeypatch.setattr(main_module, "get_model_version", lambda: "test-v1")
    async with main_module.app.router.lifespan_context(main_module.app):
        transport = ASGITransport(app=main_module.app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client


async def test_health_reports_loaded_model_over_http(monkeypatch):
    async with api_client(monkeypatch) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "model_loaded": True,
            "model_version": "test-v1",
        }
        assert response.headers["X-Request-ID"]


async def test_predict_returns_contract_over_http(monkeypatch):
    async with api_client(monkeypatch) as client:
        response = await client.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] == "CHURN"
        assert body["probability"] == 0.72
        assert body["risk_level"] == "HIGH"
        assert body["model_version"] == "test-v1"
        assert body["request_id"] == response.headers["X-Request-ID"]


async def test_schema_rejects_missing_field_over_http(monkeypatch):
    async with api_client(monkeypatch) as client:
        invalid = VALID_PAYLOAD.copy()
        invalid.pop("Contract")
        response = await client.post("/predict", json=invalid)
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"][-1] == "Contract"


async def test_schema_rejects_unknown_category_over_http(monkeypatch):
    async with api_client(monkeypatch) as client:
        invalid = {**VALID_PAYLOAD, "InternetService": "Satellite"}
        response = await client.post("/predict", json=invalid)
        assert response.status_code == 422


async def test_readiness_returns_503_when_model_is_unavailable(monkeypatch):
    async with api_client(monkeypatch) as client:
        main_module.app.state.model = None
        response = await client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Model is not loaded"}


async def test_predict_returns_500_for_unexpected_inference_failure(monkeypatch):
    class BrokenModel(ApiModel):
        def predict(self, features):
            raise RuntimeError("unexpected")

    async with api_client(monkeypatch) as client:
        main_module.app.state.model = BrokenModel()
        response = await client.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 500
        assert response.json() == {"detail": "Inference failed"}


async def test_openapi_documentation_is_available():
    schema = main_module.app.openapi()
    assert "/predict" in schema["paths"]
    assert schema["paths"]["/predict"]["post"]["responses"]["422"]
