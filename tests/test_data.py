import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from churn_ml.data import split_features_target  # noqa: E402


def test_identifier_and_target_are_removed_from_features():
    data = pd.DataFrame(
        {
            "customerID": ["A", "B"],
            "tenure": [1, 10],
            "Churn": ["No", "Yes"],
        }
    )
    features, target = split_features_target(data)
    assert features.columns.tolist() == ["tenure"]
    assert target.tolist() == [0, 1]

