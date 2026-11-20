import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_data_drift import extract_summary, load_monitoring_data  # noqa: E402


def test_monitoring_datasets_have_the_same_schema(tmp_path):
    historical = pd.DataFrame(
        {
            "customerID": ["A", "B"],
            "tenure": [1, 20],
            "TotalCharges": ["20.5", "500.0"],
            "Contract": ["Month-to-month", "One year"],
            "Churn": ["Yes", "No"],
        }
    )
    current_batch = historical.drop(columns="Churn").copy()
    reference_path = tmp_path / "historical.csv"
    current_path = tmp_path / "current.csv"
    historical.to_csv(reference_path, index=False)
    current_batch.to_csv(current_path, index=False)
    reference, current = load_monitoring_data(reference_path, current_path)
    assert reference.columns.tolist() == current.columns.tolist()
    assert len(reference) > 0
    assert len(current) > 0


def test_drift_summary_uses_metric_thresholds():
    snapshot = {
        "metrics": [
            {
                "metric_name": "DriftedColumnsCount(drift_share=0.5)",
                "config": {"drift_share": 0.5},
                "value": {"count": 1.0, "share": 0.5},
            },
            {
                "metric_name": "ValueDrift(column=tenure)",
                "config": {"column": "tenure", "threshold": 0.1},
                "value": 0.25,
            },
            {
                "metric_name": "ValueDrift(column=gender)",
                "config": {"column": "gender", "threshold": 0.1},
                "value": 0.01,
            },
        ]
    }
    summary = extract_summary(snapshot)
    assert summary["dataset_drift_detected"] is True
    assert summary["drifted_columns"] == ["tenure"]
    assert summary["column_scores"]["tenure"]["score"] == 0.25
