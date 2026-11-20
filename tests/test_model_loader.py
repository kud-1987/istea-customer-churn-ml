import json

import joblib
from sklearn.dummy import DummyClassifier

import app.model_loader as model_loader


def test_model_artifact_loads_with_inference_methods(tmp_path, monkeypatch):
    artifact = tmp_path / "candidate.joblib"
    selection = tmp_path / "selection.json"
    estimator = DummyClassifier(strategy="most_frequent").fit([[0], [1]], [0, 1])
    joblib.dump(estimator, artifact)
    selection.write_text(json.dumps({"registered_model_version": "test-v1"}))
    monkeypatch.setenv("MODEL_PATH", str(artifact))
    monkeypatch.setattr(model_loader, "SELECTION_PATH", selection)
    model = model_loader.load_model()
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert model_loader.get_model_version() == "test-v1"
