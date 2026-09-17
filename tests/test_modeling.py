import sys
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from churn_ml.modeling import make_pipeline  # noqa: E402


def test_pipeline_handles_numeric_and_categorical_features():
    features = pd.DataFrame(
        {
            "tenure": [1, 2, 20, 30],
            "contract": ["Month", "Month", "Year", "Year"],
        }
    )
    target = pd.Series([1, 1, 0, 0])
    model = make_pipeline(features, LogisticRegression(max_iter=1000))
    model.fit(features, target)
    probabilities = model.predict_proba(features)[:, 1]
    assert len(probabilities) == len(features)
    assert ((probabilities >= 0) & (probabilities <= 1)).all()

