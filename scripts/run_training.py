import json
import os
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from mlflow.models import infer_signature

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from churn_ml.data import load_historical, stratified_split  # noqa: E402
from churn_ml.modeling import (  # noqa: E402
    choose_candidate,
    evaluate,
    experiment_catalog,
    make_pipeline,
)


def configure_mlflow():
    if os.getenv("DAGSHUB_REPO"):
        import dagshub

        dagshub.init(
            repo_owner=os.getenv("DAGSHUB_OWNER", "kud-1987"),
            repo_name=os.environ["DAGSHUB_REPO"],
            mlflow=True,
        )
        mlflow.set_experiment(
            os.getenv("MLFLOW_EXPERIMENT_NAME", "customer-churn-entrega-1")
        )
        return

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", (ROOT / "mlruns").resolve().as_uri())
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "customer-churn-entrega-1"))


def main():
    params = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
    data = load_historical(ROOT / params["data"]["path"])
    x_train, x_test, y_train, y_test = stratified_split(
        data,
        test_size=params["split"]["test_size"],
        random_state=params["split"]["random_state"],
    )
    configure_mlflow()

    reports = ROOT / "reports"
    models = ROOT / "models"
    reports.mkdir(exist_ok=True)
    models.mkdir(exist_ok=True)

    result_rows = []
    trained_models = {}
    run_ids = {}
    logged_model_uris = {}
    matrices = {}

    for experiment in experiment_catalog(params["split"]["random_state"]):
        model = make_pipeline(x_train, experiment.estimator)
        with mlflow.start_run(run_name=experiment.name) as run:
            model.fit(x_train, y_train)
            metrics, matrix = evaluate(model, x_test, y_test)
            mlflow.log_params({"family": experiment.family, **experiment.params})
            mlflow.log_param("test_size", params["split"]["test_size"])
            mlflow.log_param("random_state", params["split"]["random_state"])
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(ROOT / "params.yaml"))
            input_example = x_train.head(3)
            signature = infer_signature(input_example, model.predict(input_example))
            model_info = mlflow.sklearn.log_model(
                model,
                name="model",
                input_example=input_example,
                signature=signature,
            )

            result_rows.append(
                {
                    "experiment": experiment.name,
                    "family": experiment.family,
                    "run_id": run.info.run_id,
                    **metrics,
                }
            )
            trained_models[experiment.name] = model
            run_ids[experiment.name] = run.info.run_id
            logged_model_uris[experiment.name] = model_info.model_uri
            matrices[experiment.name] = matrix

    results = pd.DataFrame(result_rows).sort_values("recall", ascending=False)
    candidate = choose_candidate(results, params["selection"]["minimum_roc_auc"])
    candidate_name = candidate["experiment"]
    candidate_model = trained_models[candidate_name]
    candidate_run_id = run_ids[candidate_name]
    model_name = os.getenv("MLFLOW_MODEL_NAME", "customer-churn-candidate")

    model_uri = logged_model_uris[candidate_name]
    registered = mlflow.register_model(model_uri=model_uri, name=model_name)
    joblib.dump(candidate_model, models / "candidate.joblib")

    results.to_csv(reports / "model_comparison.csv", index=False)
    pd.DataFrame(
        matrices[candidate_name],
        index=["actual_no_churn", "actual_churn"],
        columns=["predicted_no_churn", "predicted_churn"],
    ).to_csv(reports / "confusion_matrix.csv")

    metric_names = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    metrics = {name: float(candidate[name]) for name in metric_names}
    (reports / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    selection = {
        "candidate_experiment": candidate_name,
        "candidate_run_id": candidate_run_id,
        "registered_model_name": model_name,
        "registered_model_version": str(registered.version),
        "selection_rule": "Highest churn recall among runs meeting minimum ROC-AUC; ROC-AUC and F1 break ties.",
        "minimum_roc_auc": params["selection"]["minimum_roc_auc"],
        "metrics": metrics,
    }
    (reports / "selection.json").write_text(
        json.dumps(selection, indent=2), encoding="utf-8"
    )
    print(results.to_string(index=False))
    print(f"Selected candidate: {candidate_name} (run {candidate_run_id})")


if __name__ == "__main__":
    main()
