import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status

from app.inference import predict_churn
from app.model_loader import get_model_version, load_model
from app.schemas import HealthResponse, PredictionRequest, PredictionResponse


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    app.state.model_version = get_model_version()
    yield
    app.state.model = None


app = FastAPI(
    title="Customer Churn Prediction API",
    description="API de inferencia del proyecto integrador de Mineria de Datos.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health(request: Request) -> HealthResponse:
    loaded = getattr(request.app.state, "model", None) is not None
    return HealthResponse(
        status="ok" if loaded else "not_ready",
        model_loaded=loaded,
        model_version=getattr(request.app.state, "model_version", "unknown"),
    )


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
def readiness(request: Request) -> HealthResponse:
    response = health(request)
    if not response.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return response


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available",
        )
    request_id = str(uuid4())
    try:
        result = predict_churn(model, payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Inference failed for request_id=%s", request_id)
        raise HTTPException(status_code=500, detail="Inference failed") from exc
    return PredictionResponse(
        **result,
        model_version=request.app.state.model_version,
        request_id=request_id,
    )
