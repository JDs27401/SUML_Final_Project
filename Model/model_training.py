from __future__ import annotations

from datetime import datetime
from pathlib import Path
from pickle import UnpicklingError

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from Data.football_data import (
    PROJECT_ROOT,
    build_training_dataset,
    get_available_countries,
    get_available_teams,
    get_available_tournaments,
    get_completed_matches,
    load_results_dataframe,
)


MODEL_DIRECTORY = PROJECT_ROOT / "Model" / "artifacts"
MODEL_FILE_PATH = MODEL_DIRECTORY / "football_match_linear_regression.joblib"
BROKEN_MODEL_FILE_PATH = MODEL_DIRECTORY / "football_match_linear_regression.broken.joblib"

NUMERIC_FEATURES = [
    "home_winrate",
    "home_gf",
    "home_ga",
    "away_winrate",
    "away_gf",
    "away_ga",
]
CATEGORICAL_FEATURES = ["tournament", "country", "neutral"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def create_linear_regression_pipeline() -> Pipeline:
    preprocessing_pipeline = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessing", preprocessing_pipeline),
            ("regression", LinearRegression()),
        ]
    )


def train_and_save_model(force_retrain: bool = False) -> dict[str, object]:
    if MODEL_FILE_PATH.exists() and not force_retrain:
        try:
            return joblib.load(MODEL_FILE_PATH)
        except (AttributeError, EOFError, ImportError, ModuleNotFoundError, UnpicklingError, ValueError):
            move_incompatible_model_artifact()

    results_dataframe = load_results_dataframe()
    completed_matches = get_completed_matches(results_dataframe)
    features_dataframe, target_series = build_training_dataset(completed_matches)

    train_features, test_features, train_target, test_target = train_test_split(
        features_dataframe,
        target_series,
        test_size=0.2,
        random_state=42,
    )

    model_pipeline = create_linear_regression_pipeline()
    model_pipeline.fit(train_features, train_target)
    predictions = model_pipeline.predict(test_features)

    model_package: dict[str, object] = {
        "model": model_pipeline,
        "features": MODEL_FEATURES,
        "metrics": {
            "mean_absolute_error": float(mean_absolute_error(test_target, predictions)),
            "r2_score": float(r2_score(test_target, predictions)),
            "training_rows": int(len(features_dataframe)),
            "test_rows": int(len(test_features)),
        },
        "metadata": {
            "trained_at": datetime.now().isoformat(timespec="seconds"),
            "model_type": "LinearRegression",
            "target": "home_score - away_score",
            "teams": get_available_teams(results_dataframe),
            "tournaments": get_available_tournaments(results_dataframe),
            "countries": get_available_countries(results_dataframe),
        },
    }

    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_package, MODEL_FILE_PATH)
    return model_package


def move_incompatible_model_artifact() -> None:
    if not MODEL_FILE_PATH.exists():
        return

    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    if BROKEN_MODEL_FILE_PATH.exists():
        BROKEN_MODEL_FILE_PATH.unlink()
    MODEL_FILE_PATH.replace(BROKEN_MODEL_FILE_PATH)
