from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class Experiment:
    name: str
    family: str
    estimator: object
    params: dict


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric = features.select_dtypes(include=[np.number]).columns.tolist()
    categorical = features.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ]
    )


def experiment_catalog(random_state: int) -> list[Experiment]:
    return [
        Experiment(
            "dummy_most_frequent",
            "baseline",
            DummyClassifier(strategy="most_frequent"),
            {"strategy": "most_frequent"},
        ),
        Experiment(
            "logistic_balanced_c1",
            "linear",
            LogisticRegression(
                C=1.0,
                class_weight="balanced",
                max_iter=2000,
                random_state=random_state,
            ),
            {"C": 1.0, "class_weight": "balanced"},
        ),
        Experiment(
            "logistic_balanced_c05",
            "linear",
            LogisticRegression(
                C=0.5,
                class_weight="balanced",
                max_iter=2000,
                random_state=random_state,
            ),
            {"C": 0.5, "class_weight": "balanced"},
        ),
        Experiment(
            "random_forest_balanced_200",
            "tree",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=None,
                min_samples_leaf=2,
                class_weight="balanced",
                n_jobs=-1,
                random_state=random_state,
            ),
            {"n_estimators": 200, "max_depth": None, "min_samples_leaf": 2},
        ),
        Experiment(
            "random_forest_depth_10",
            "tree",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=10,
                min_samples_leaf=2,
                class_weight="balanced",
                n_jobs=-1,
                random_state=random_state,
            ),
            {"n_estimators": 300, "max_depth": 10, "min_samples_leaf": 2},
        ),
        Experiment(
            "random_forest_depth_7",
            "tree",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=7,
                min_samples_leaf=4,
                class_weight="balanced",
                n_jobs=-1,
                random_state=random_state,
            ),
            {"n_estimators": 300, "max_depth": 7, "min_samples_leaf": 4},
        ),
    ]


def make_pipeline(features: pd.DataFrame, estimator) -> Pipeline:
    return Pipeline(
        [
            ("preprocessing", build_preprocessor(features)),
            ("classifier", estimator),
        ]
    )


def evaluate(model: Pipeline, features: pd.DataFrame, target: pd.Series):
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    metrics = {
        "accuracy": accuracy_score(target, predictions),
        "precision": precision_score(target, predictions, zero_division=0),
        "recall": recall_score(target, predictions, zero_division=0),
        "f1": f1_score(target, predictions, zero_division=0),
        "roc_auc": roc_auc_score(target, probabilities),
    }
    matrix = confusion_matrix(target, predictions)
    return metrics, matrix


def choose_candidate(results: pd.DataFrame, minimum_roc_auc: float) -> pd.Series:
    eligible = results[results["roc_auc"] >= minimum_roc_auc]
    if eligible.empty:
        eligible = results[results["family"] != "baseline"]
    return eligible.sort_values(["recall", "roc_auc", "f1"], ascending=False).iloc[0]

