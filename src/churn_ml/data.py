from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


TARGET = "Churn"
ID_COLUMN = "customerID"


def load_historical(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = {TARGET, ID_COLUMN}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    data = data.copy()
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
    return data


def split_features_target(data: pd.DataFrame):
    features = data.drop(columns=[TARGET, ID_COLUMN])
    target = data[TARGET].map({"No": 0, "Yes": 1})
    if target.isna().any():
        raise ValueError("Churn must contain only Yes or No")
    return features, target


def stratified_split(data: pd.DataFrame, test_size: float, random_state: int):
    features, target = split_features_target(data)
    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )

