import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(ROOT / "src"))

from churn_ml.data import load_historical  # noqa: E402


DATA_PATH = ROOT / "data/raw/customer_churn_historical.csv"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"


def main():
    REPORTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    data = load_historical(DATA_PATH)

    summary = {
        "rows": int(data.shape[0]),
        "columns": int(data.shape[1]),
        "duplicate_rows": int(data.duplicated().sum()),
        "duplicate_customer_ids": int(data["customerID"].duplicated().sum()),
        "missing_by_column": {k: int(v) for k, v in data.isna().sum().items()},
        "target_counts": {k: int(v) for k, v in data["Churn"].value_counts().items()},
        "target_rate": float((data["Churn"] == "Yes").mean()),
        "numeric_summary": data.select_dtypes(include="number").describe().round(3).to_dict(),
        "quality_findings": [
            "customerID is an identifier and is excluded from predictors.",
            "TotalCharges contains missing values handled inside the pipeline.",
            "The target is imbalanced, so accuracy is not used alone.",
        ],
    }
    (REPORTS / "eda_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    ax = sns.countplot(data=data, x="Churn", hue="Churn", legend=False)
    ax.set(title="Distribucion de la variable Churn", xlabel="Churn", ylabel="Clientes")
    plt.tight_layout()
    plt.savefig(FIGURES / "target_distribution.png", dpi=160)
    plt.close()

    contract = pd.crosstab(data["Contract"], data["Churn"], normalize="index")
    contract.plot(kind="bar", stacked=True, figsize=(8, 4), color=["#4C78A8", "#E45756"])
    plt.title("Proporcion de churn por tipo de contrato")
    plt.xlabel("Contrato")
    plt.ylabel("Proporcion")
    plt.legend(title="Churn")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES / "churn_by_contract.png", dpi=160)
    plt.close()

    data[["tenure", "MonthlyCharges", "TotalCharges"]].hist(
        bins=30, figsize=(10, 6), color="#4C78A8", edgecolor="white"
    )
    plt.suptitle("Distribuciones de variables numericas")
    plt.tight_layout()
    plt.savefig(FIGURES / "numeric_distributions.png", dpi=160)
    plt.close()

    print(f"EDA generado en {REPORTS}")


if __name__ == "__main__":
    main()
