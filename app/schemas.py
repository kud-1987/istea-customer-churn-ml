from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


YesNo = Literal["Yes", "No"]
InternetAddOn = Literal["Yes", "No", "No internet service"]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gender: Literal["Female", "Male"]
    SeniorCitizen: Literal[0, 1]
    Partner: YesNo
    Dependents: YesNo
    tenure: int = Field(ge=0, le=100)
    PhoneService: YesNo
    MultipleLines: Literal["Yes", "No", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: InternetAddOn
    OnlineBackup: InternetAddOn
    DeviceProtection: InternetAddOn
    TechSupport: InternetAddOn
    StreamingTV: InternetAddOn
    StreamingMovies: InternetAddOn
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: YesNo
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float | None = Field(default=None, ge=0)


class PredictionResponse(BaseModel):
    prediction: Literal[0, 1]
    churn: Literal["No", "Yes"]
    probability: float = Field(ge=0, le=1)
    risk_level: Literal["low", "medium", "high"]
    model_version: str
    request_id: str


class HealthResponse(BaseModel):
    status: Literal["ok", "not_ready"]
    model_loaded: bool
    model_version: str
