import logging
import os
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status

from app.inference import predict_churn
from app.model_loader import get_model_version, load_model
from app.schemas import HealthResponse, PredictionRequest, PredictionResponse


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.model = load_model()
    app.state.model_version = get_model_version()
    logger.info("service_started model_version=%s", app.state.model_version)
    yield
    logger.info("service_stopped model_version=%s", app.state.model_version)
    app.state.model = None


app = FastAPI(
    title="Customer Churn Prediction API",
    description="API de inferencia del proyecto integrador de Mineria de Datos.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        latency_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "request_failed request_id=%s method=%s path=%s latency_ms=%.2f model_version=%s",
            request_id,
            request.method,
            request.url.path,
            latency_ms,
            getattr(request.app.state, "model_version", "unknown"),
        )
        raise
    latency_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed request_id=%s method=%s path=%s status_code=%s latency_ms=%.2f model_version=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
        getattr(request.app.state, "model_version", "unknown"),
    )
    return response


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health(request: Request) -> HealthResponse:
    loaded = getattr(request.app.state, "model", None) is not None
    return HealthResponse(
        status="ok" if loaded else "not_ready",
        model_loaded=loaded,
        model_version=getattr(request.app.state, "model_version", "unknown"),
    )


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
async def readiness(request: Request) -> HealthResponse:
    response = await health(request)
    if not response.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return response


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
async def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available",
        )
    request_id = getattr(request.state, "request_id", str(uuid4()))
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
