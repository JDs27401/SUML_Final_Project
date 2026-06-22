from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "Data"
RESULTS_FILE_PATH = DATA_DIRECTORY / "results.csv"
FORM_MATCH_LIMIT = 20


@dataclass(frozen=True)
class TeamRecentStatistics:
    winrate: float
    average_goals_for: float
    average_goals_against: float
    matches_used: int


def load_results_dataframe() -> pd.DataFrame:
    results_dataframe = pd.read_csv(RESULTS_FILE_PATH)
    results_dataframe["date"] = pd.to_datetime(results_dataframe["date"], errors="coerce")
    results_dataframe["home_score"] = pd.to_numeric(results_dataframe["home_score"], errors="coerce")
    results_dataframe["away_score"] = pd.to_numeric(results_dataframe["away_score"], errors="coerce")
    results_dataframe["neutral"] = results_dataframe["neutral"].astype(bool)
    return results_dataframe


def get_completed_matches(results_dataframe: pd.DataFrame) -> pd.DataFrame:
    completed_matches = results_dataframe.dropna(subset=["date", "home_score", "away_score"]).copy()
    completed_matches["home_score"] = completed_matches["home_score"].astype(int)
    completed_matches["away_score"] = completed_matches["away_score"].astype(int)
    return completed_matches.sort_values("date").reset_index(drop=True)


def get_available_teams(results_dataframe: pd.DataFrame) -> list[str]:
    all_teams = set(results_dataframe["home_team"].dropna()) | set(results_dataframe["away_team"].dropna())
    return sorted(all_teams)


def get_available_tournaments(results_dataframe: pd.DataFrame) -> list[str]:
    return sorted(results_dataframe["tournament"].dropna().unique())


def get_available_countries(results_dataframe: pd.DataFrame) -> list[str]:
    return sorted(results_dataframe["country"].dropna().unique())


def calculate_recent_team_statistics(
    completed_matches: pd.DataFrame,
    team_name: str,
    match_date: date | pd.Timestamp,
    match_limit: int = FORM_MATCH_LIMIT,
) -> TeamRecentStatistics:
    prediction_date = pd.Timestamp(match_date)
    team_matches = completed_matches[
        (completed_matches["date"] < prediction_date)
        & (
            (completed_matches["home_team"] == team_name)
            | (completed_matches["away_team"] == team_name)
        )
    ].tail(match_limit)

    if team_matches.empty:
        return TeamRecentStatistics(
            winrate=0.0,
            average_goals_for=0.0,
            average_goals_against=0.0,
            matches_used=0,
        )

    wins = 0
    goals_for = 0
    goals_against = 0

    for _, match in team_matches.iterrows():
        is_home_team = match["home_team"] == team_name
        team_goals = int(match["home_score"] if is_home_team else match["away_score"])
        opponent_goals = int(match["away_score"] if is_home_team else match["home_score"])

        goals_for += team_goals
        goals_against += opponent_goals
        wins += int(team_goals > opponent_goals)

    matches_used = len(team_matches)
    return TeamRecentStatistics(
        winrate=wins / matches_used,
        average_goals_for=goals_for / matches_used,
        average_goals_against=goals_against / matches_used,
        matches_used=matches_used,
    )


def build_training_dataset(completed_matches: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_rows: list[dict[str, object]] = []
    target_values: list[int] = []
    team_histories: dict[str, list[dict[str, float]]] = {}

    for _, match in completed_matches.sort_values("date").iterrows():
        home_team = match["home_team"]
        away_team = match["away_team"]
        home_history = team_histories.get(home_team, [])[-FORM_MATCH_LIMIT:]
        away_history = team_histories.get(away_team, [])[-FORM_MATCH_LIMIT:]

        if home_history and away_history:
            feature_rows.append(
                {
                    "home_winrate": _calculate_average(home_history, "win"),
                    "home_gf": _calculate_average(home_history, "goals_for"),
                    "home_ga": _calculate_average(home_history, "goals_against"),
                    "away_winrate": _calculate_average(away_history, "win"),
                    "away_gf": _calculate_average(away_history, "goals_for"),
                    "away_ga": _calculate_average(away_history, "goals_against"),
                    "tournament": match["tournament"],
                    "country": match["country"],
                    "neutral": bool(match["neutral"]),
                }
            )
            target_values.append(int(match["home_score"]) - int(match["away_score"]))

        home_goals = int(match["home_score"])
        away_goals = int(match["away_score"])
        team_histories.setdefault(home_team, []).append(
            {
                "win": float(home_goals > away_goals),
                "goals_for": float(home_goals),
                "goals_against": float(away_goals),
            }
        )
        team_histories.setdefault(away_team, []).append(
            {
                "win": float(away_goals > home_goals),
                "goals_for": float(away_goals),
                "goals_against": float(home_goals),
            }
        )

    features_dataframe = pd.DataFrame(feature_rows)
    target_series = pd.Series(target_values, name="home_goal_difference")
    return features_dataframe, target_series


def _calculate_average(history: list[dict[str, float]], metric_name: str) -> float:
    return sum(match[metric_name] for match in history) / len(history)
