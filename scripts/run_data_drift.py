import json
import sys
from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from churn_ml.data import ID_COLUMN, TARGET, load_historical  # noqa: E402


REFERENCE_PATH = ROOT / "data" / "raw" / "customer_churn_historical.csv"
CURRENT_PATH = ROOT / "data" / "production" / "customer_churn_current.csv"
REPORT_PATH = ROOT / "reports" / "drift_report.html"
SUMMARY_PATH = ROOT / "reports" / "drift_summary.json"


def load_monitoring_data(
    reference_path: Path = REFERENCE_PATH,
    current_path: Path = CURRENT_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    reference = load_historical(reference_path).drop(columns=[TARGET, ID_COLUMN])
    current = pd.read_csv(current_path).drop(columns=[ID_COLUMN])
    current["TotalCharges"] = pd.to_numeric(current["TotalCharges"], errors="coerce")
    if set(reference.columns) != set(current.columns):
        missing = sorted(set(reference.columns) - set(current.columns))
        extra = sorted(set(current.columns) - set(reference.columns))
        raise ValueError(f"Monitoring schema mismatch; missing={missing}, extra={extra}")
    return reference, current[reference.columns]


def extract_summary(snapshot: dict) -> dict:
    metrics = snapshot.get("metrics", [])
    drifted_columns = []
    column_scores = {}
    dataset_drift = False
    share = 0.0
    for metric in metrics:
        metric_name = metric.get("metric_name", "")
        config = metric.get("config", {})
        value = metric.get("value", {})
        if "DriftedColumnsCount" in metric_name and isinstance(value, dict):
            share = float(value.get("share", 0.0))
            dataset_drift = share >= float(config.get("drift_share", 0.5))
        if "ValueDrift" in metric_name and not isinstance(value, dict):
            column = config.get("column")
            score = float(value)
            threshold = float(config.get("threshold", 0.1))
            if column:
                column_scores[column] = {"score": score, "threshold": threshold}
            if column and score >= threshold:
                drifted_columns.append(column)
    return {
        "dataset_drift_detected": dataset_drift,
        "drifted_columns_share": share,
        "drifted_columns": sorted(set(drifted_columns)),
        "column_scores": column_scores,
        "interpretation": (
            "El drift es una senal para investigar. No implica reentrenamiento automatico; "
            "se debe confirmar el contexto de negocio y evaluar performance con etiquetas cuando esten disponibles."
        ),
    }


def main() -> None:
    reference, current = load_monitoring_data()
    report = Report([DataDriftPreset()])
    snapshot = report.run(reference_data=reference, current_data=current)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    snapshot.save_html(str(REPORT_PATH))
    summary = extract_summary(snapshot.dict())
    summary.update({"reference_rows": len(reference), "current_rows": len(current)})
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"HTML report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
