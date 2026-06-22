from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Data.football_data import (  # noqa: E402
    get_available_countries,
    get_available_teams,
    get_available_tournaments,
    load_results_dataframe,
)
from Model.model_training import train_and_save_model  # noqa: E402
from Model.predictor import predict_match_result  # noqa: E402


app = FastAPI(
    title="Football Match Predictor API",
    version="1.3.2",
    description="API do przewidywania wyniku meczu pilkarskiego za pomoca regresji liniowej.",
)


class MatchPredictionRequest(BaseModel):
    home_team: str = Field(..., min_length=1)
    away_team: str = Field(..., min_length=1)
    tournament: str = Field(..., min_length=1)
    match_country: str = Field(..., min_length=1)
    is_neutral_ground: bool
    match_date: date


class MatchPredictionResponse(BaseModel):
    predicted_label: str
    predicted_outcome: str
    predicted_winner: str | None
    predicted_home_goal_difference: float
    predicted_home_goals: float
    predicted_away_goals: float
    home_recent_matches_used: int
    away_recent_matches_used: int
    team_statistics: dict[str, dict[str, float | int]]
    input_features: dict[str, Any]


@app.get("/health")
def get_health_status() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata")
def get_prediction_metadata() -> dict[str, Any]:
    results_dataframe = load_results_dataframe()
    model_package = train_and_save_model()
    return {
        "teams": get_available_teams(results_dataframe),
        "tournaments": get_available_tournaments(results_dataframe),
        "countries": get_available_countries(results_dataframe),
        "model": {
            "metadata": model_package["metadata"],
            "metrics": model_package["metrics"],
        },
    }


@app.post("/predict", response_model=MatchPredictionResponse)
def create_match_prediction(request: MatchPredictionRequest) -> MatchPredictionResponse:
    try:
        prediction = predict_match_result(
            home_team=request.home_team,
            away_team=request.away_team,
            tournament=request.tournament,
            match_country=request.match_country,
            is_neutral_ground=request.is_neutral_ground,
            match_date=request.match_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return MatchPredictionResponse(
        predicted_label=prediction.predicted_label,
        predicted_outcome=prediction.predicted_outcome,
        predicted_winner=prediction.predicted_winner,
        predicted_home_goal_difference=prediction.predicted_home_goal_difference,
        predicted_home_goals=prediction.predicted_home_goals,
        predicted_away_goals=prediction.predicted_away_goals,
        home_recent_matches_used=prediction.home_recent_matches_used,
        away_recent_matches_used=prediction.away_recent_matches_used,
        team_statistics=prediction.team_statistics,
        input_features=prediction.input_features,
    )


@app.post("/retrain")
def retrain_prediction_model() -> dict[str, Any]:
    model_package = train_and_save_model(force_retrain=True)
    return {
        "status": "retrained",
        "metadata": model_package["metadata"],
        "metrics": model_package["metrics"],
    }
