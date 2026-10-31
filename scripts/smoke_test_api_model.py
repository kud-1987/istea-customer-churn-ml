from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.inference import predict_churn  # noqa: E402
from app.model_loader import load_model  # noqa: E402
from app.schemas import PredictionRequest  # noqa: E402


def main():
    scoring = pd.read_csv(ROOT / "data" / "scoring" / "scoring_batch.csv")
    payload = PredictionRequest(**scoring.iloc[0].drop(labels=["customerID"]).to_dict())
    result = predict_churn(load_model(), payload)
    print("Real model smoke test: OK")
    print(result)


if __name__ == "__main__":
    main()
