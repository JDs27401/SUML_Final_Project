from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from Data.football_data import (
    calculate_recent_team_statistics,
    get_completed_matches,
    load_results_dataframe,
)
from Model.model_training import MODEL_FEATURES, train_and_save_model


DRAW_THRESHOLD = 0.35


@dataclass(frozen=True)
class MatchPrediction:
    predicted_label: str
    predicted_outcome: str
    predicted_winner: str | None
    predicted_home_goal_difference: float
    predicted_home_goals: float
    predicted_away_goals: float
    home_recent_matches_used: int
    away_recent_matches_used: int
    team_statistics: dict[str, dict[str, float | int]]
    input_features: dict[str, object]


def predict_match_result(
    home_team: str,
    away_team: str,
    tournament: str,
    match_country: str,
    is_neutral_ground: bool,
    match_date: date,
) -> MatchPrediction:
    if home_team == away_team:
        raise ValueError("Druzyna gospodarzy i druzyna gosci musza byc rozne.")

    results_dataframe = load_results_dataframe()
    completed_matches = get_completed_matches(results_dataframe)
    known_teams = set(results_dataframe["home_team"]) | set(results_dataframe["away_team"])

    if home_team not in known_teams:
        raise ValueError(f"Model nie posiada danych dla druzyny: {home_team}.")
    if away_team not in known_teams:
        raise ValueError(f"Model nie posiada danych dla druzyny: {away_team}.")

    home_statistics = calculate_recent_team_statistics(completed_matches, home_team, match_date)
    away_statistics = calculate_recent_team_statistics(completed_matches, away_team, match_date)

    if home_statistics.matches_used == 0:
        raise ValueError(f"Brak historycznych meczow druzyny {home_team} przed wskazana data.")
    if away_statistics.matches_used == 0:
        raise ValueError(f"Brak historycznych meczow druzyny {away_team} przed wskazana data.")

    input_features = {
        "home_winrate": home_statistics.winrate,
        "home_gf": home_statistics.average_goals_for,
        "home_ga": home_statistics.average_goals_against,
        "away_winrate": away_statistics.winrate,
        "away_gf": away_statistics.average_goals_for,
        "away_ga": away_statistics.average_goals_against,
        "tournament": tournament,
        "country": match_country,
        "neutral": is_neutral_ground,
    }

    model_package = train_and_save_model()
    model = model_package["model"]
    feature_dataframe = pd.DataFrame([input_features], columns=MODEL_FEATURES)
    predicted_goal_difference = float(model.predict(feature_dataframe)[0])
    predicted_outcome = classify_goal_difference(predicted_goal_difference)
    predicted_home_goals, predicted_away_goals = estimate_team_goal_counts(
        predicted_goal_difference=predicted_goal_difference,
        home_average_goals_for=home_statistics.average_goals_for,
        away_average_goals_for=away_statistics.average_goals_for,
    )

    return MatchPrediction(
        predicted_label=create_prediction_label(
            predicted_outcome=predicted_outcome,
            home_team=home_team,
            away_team=away_team,
        ),
        predicted_outcome=predicted_outcome,
        predicted_winner=get_predicted_winner(
            predicted_outcome=predicted_outcome,
            home_team=home_team,
            away_team=away_team,
        ),
        predicted_home_goal_difference=predicted_goal_difference,
        predicted_home_goals=predicted_home_goals,
        predicted_away_goals=predicted_away_goals,
        home_recent_matches_used=home_statistics.matches_used,
        away_recent_matches_used=away_statistics.matches_used,
        team_statistics={
            home_team: {
                "winrate": home_statistics.winrate,
                "average_goals_for": home_statistics.average_goals_for,
                "average_goals_against": home_statistics.average_goals_against,
                "matches_used": home_statistics.matches_used,
            },
            away_team: {
                "winrate": away_statistics.winrate,
                "average_goals_for": away_statistics.average_goals_for,
                "average_goals_against": away_statistics.average_goals_against,
                "matches_used": away_statistics.matches_used,
            },
        },
        input_features=input_features,
    )


def classify_goal_difference(predicted_goal_difference: float) -> str:
    if predicted_goal_difference > DRAW_THRESHOLD:
        return "home_win"
    if predicted_goal_difference < -DRAW_THRESHOLD:
        return "away_win"
    return "draw"


def create_prediction_label(predicted_outcome: str, home_team: str, away_team: str) -> str:
    if predicted_outcome == "home_win":
        return f"{home_team} wygra"
    if predicted_outcome == "away_win":
        return f"{away_team} wygra"
    return "Remis"


def get_predicted_winner(predicted_outcome: str, home_team: str, away_team: str) -> str | None:
    if predicted_outcome == "home_win":
        return home_team
    if predicted_outcome == "away_win":
        return away_team
    return None


def estimate_team_goal_counts(
    predicted_goal_difference: float,
    home_average_goals_for: float,
    away_average_goals_for: float,
) -> tuple[float, float]:
    expected_total_goals = max(0.5, home_average_goals_for + away_average_goals_for)
    predicted_home_goals = max(0.0, (expected_total_goals + predicted_goal_difference) / 2)
    predicted_away_goals = max(0.0, (expected_total_goals - predicted_goal_difference) / 2)
    return predicted_home_goals, predicted_away_goals
