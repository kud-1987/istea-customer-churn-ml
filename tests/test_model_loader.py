from app.model_loader import get_model_version, load_model


def test_real_model_artifact_loads_with_inference_methods():
    model = load_model()
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert get_model_version() == "1"
