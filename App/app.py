from __future__ import annotations

import sys
from datetime import date
from typing import Any

import requests
import streamlit as st


MINIMUM_PYTHON_VERSION = (3, 14)
DEFAULT_API_URL = "http://127.0.0.1:8000"
FIRST_TEAM_HOST_OPTION = "Druzyna 1 jest gospodarzem"
SECOND_TEAM_HOST_OPTION = "Druzyna 2 jest gospodarzem"
NEUTRAL_GROUND_OPTION = "Brak gospodarza - boisko neutralne"


def main() -> None:
    st.set_page_config(page_title="Football Match Predictor", layout="centered")
    st.title("Football Match Predictor")
    stop_application_when_python_version_is_not_supported()

    api_url = get_api_url()
    try:
        metadata_response = load_prediction_metadata(api_url)
    except requests.RequestException as error:
        st.error(f"Nie mozna polaczyc sie z backendem API: {api_url}")
        st.code(r".\run_api.bat", language="powershell")
        st.caption(str(error))
        st.stop()

    model_details = metadata_response["model"]
    metadata = model_details["metadata"]
    metrics = model_details["metrics"]

    teams = metadata_response["teams"]
    tournaments = metadata_response["tournaments"]
    countries = metadata_response["countries"]

    with st.sidebar:
        st.subheader("Model")
        st.write(f"Typ: {metadata['model_type']}")
        st.write(f"Wiersze treningowe: {metrics['training_rows']}")
        st.write(f"MAE: {metrics['mean_absolute_error']:.3f}")
        st.write(f"R2: {metrics['r2_score']:.3f}")

        if st.button("Przetrenuj model"):
            retrain_model(api_url)
            st.cache_data.clear()
            st.rerun()

    with st.form("prediction_form"):
        first_team = st.selectbox("Druzyna 1", teams, key="first_team_select")
        second_team = st.selectbox("Druzyna 2", teams, key="second_team_select")
        host_selection = st.radio(
            "Gospodarz meczu",
            [FIRST_TEAM_HOST_OPTION, SECOND_TEAM_HOST_OPTION, NEUTRAL_GROUND_OPTION],
            horizontal=True,
        )
        tournament = st.selectbox("Turniej", tournaments, index=get_default_index(tournaments, "Friendly"))
        match_country = st.selectbox("Kraj rozegrania meczu", countries, index=0)
        match_date = st.date_input("Data meczu", value=date.today())

        submitted = st.form_submit_button("Przewidz wynik")

    if submitted:
        match_team_setup = build_match_team_setup(first_team, second_team, host_selection)
        show_prediction(
            home_team=match_team_setup["home_team"],
            away_team=match_team_setup["away_team"],
            first_selected_team=first_team,
            second_selected_team=second_team,
            tournament=tournament,
            match_country=match_country,
            is_neutral_ground=match_team_setup["is_neutral_ground"],
            match_date=match_date,
            api_url=api_url,
        )


def get_api_url() -> str:
    configured_api_url = st.query_params.get("api_url", DEFAULT_API_URL)
    return configured_api_url.rstrip("/")


@st.cache_data(show_spinner="Laczenie z API i wczytywanie metadanych...")
def load_prediction_metadata(api_url: str) -> dict[str, Any]:
    response = requests.get(f"{api_url}/metadata", timeout=120)
    response.raise_for_status()
    return response.json()


def retrain_model(api_url: str) -> None:
    response = requests.post(f"{api_url}/retrain", timeout=180)
    response.raise_for_status()


def stop_application_when_python_version_is_not_supported() -> None:
    if sys.version_info >= MINIMUM_PYTHON_VERSION:
        return

    st.error(
        "Aplikacja wymaga Python 3.14. Uruchom ja interpreterem z projektowego "
        "srodowiska `.venv`."
    )
    st.code(r".venv\Scripts\python.exe -m streamlit run App\app.py", language="powershell")
    st.stop()


def get_default_index(options: list[str], default_value: str) -> int:
    return options.index(default_value) if default_value in options else 0


def build_match_team_setup(
    first_team: str,
    second_team: str,
    host_selection: str,
) -> dict[str, str | bool]:
    if host_selection == SECOND_TEAM_HOST_OPTION:
        return {
            "home_team": second_team,
            "away_team": first_team,
            "is_neutral_ground": False,
        }

    if host_selection == NEUTRAL_GROUND_OPTION:
        return {
            "home_team": first_team,
            "away_team": second_team,
            "is_neutral_ground": True,
        }

    return {
        "home_team": first_team,
        "away_team": second_team,
        "is_neutral_ground": False,
    }


def show_prediction(
    home_team: str,
    away_team: str,
    first_selected_team: str,
    second_selected_team: str,
    tournament: str,
    match_country: str,
    is_neutral_ground: bool,
    match_date: date,
    api_url: str,
) -> None:
    try:
        prediction = request_match_prediction(
            api_url=api_url,
            prediction_request={
                "home_team": home_team,
                "away_team": away_team,
                "tournament": tournament,
                "match_country": match_country,
                "is_neutral_ground": is_neutral_ground,
                "match_date": match_date.isoformat(),
            },
        )
    except requests.HTTPError as error:
        st.error(get_error_message_from_response(error.response))
        return
    except requests.RequestException as error:
        st.error(f"Nie mozna polaczyc sie z API: {error}")
        return

    show_prediction_summary(
        prediction=prediction,
        first_displayed_team=first_selected_team,
        second_displayed_team=second_selected_team,
        model_home_team=home_team,
        model_away_team=away_team,
        is_neutral_ground=is_neutral_ground,
    )

    with st.expander("Dane techniczne predykcji"):
        st.json(prediction["input_features"])


def show_prediction_summary(
    prediction: dict[str, Any],
    first_displayed_team: str,
    second_displayed_team: str,
    model_home_team: str,
    model_away_team: str,
    is_neutral_ground: bool,
) -> None:
    predicted_winner = prediction["predicted_winner"]
    predicted_label = prediction["predicted_label"]
    displayed_goal_estimates = get_displayed_goal_estimates(
        prediction=prediction,
        first_displayed_team=first_displayed_team,
        second_displayed_team=second_displayed_team,
        model_home_team=model_home_team,
        model_away_team=model_away_team,
    )
    rounded_score = (
        f"{round(displayed_goal_estimates[first_displayed_team])}"
        f":{round(displayed_goal_estimates[second_displayed_team])}"
    )

    st.subheader(f"{first_displayed_team} vs {second_displayed_team}")
    st.success(predicted_label)

    first_metric_column, second_metric_column, third_metric_column = st.columns(3)
    first_metric_column.metric("Predykcja", predicted_winner or "Remis")
    second_metric_column.metric("Przyblizony wynik", rounded_score)
    third_metric_column.metric(
        "Przewaga wg modelu",
        f"{prediction['predicted_home_goal_difference']:.2f}",
    )

    st.write(
        "Szacowane gole: "
        f"{first_displayed_team} {displayed_goal_estimates[first_displayed_team]:.1f} : "
        f"{displayed_goal_estimates[second_displayed_team]:.1f} {second_displayed_team}"
    )

    context_label = (
        "Mecz oznaczony jako rozgrywany na boisku neutralnym."
        if is_neutral_ground
        else f"Gospodarz meczu: {model_home_team}."
    )
    st.caption(context_label)

    st.dataframe(
        build_team_statistics_table(prediction["team_statistics"]),
        hide_index=True,
        use_container_width=True,
    )


def get_displayed_goal_estimates(
    prediction: dict[str, Any],
    first_displayed_team: str,
    second_displayed_team: str,
    model_home_team: str,
    model_away_team: str,
) -> dict[str, float]:
    goal_estimates_by_model_role = {
        model_home_team: float(prediction["predicted_home_goals"]),
        model_away_team: float(prediction["predicted_away_goals"]),
    }
    return {
        first_displayed_team: goal_estimates_by_model_role[first_displayed_team],
        second_displayed_team: goal_estimates_by_model_role[second_displayed_team],
    }


def build_team_statistics_table(team_statistics: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for team_name, statistics in team_statistics.items():
        rows.append(
            {
                "Druzyna": team_name,
                "Mecze w formie": statistics["matches_used"],
                "Winrate": f"{statistics['winrate'] * 100:.1f}%",
                "Srednio strzela": f"{statistics['average_goals_for']:.2f}",
                "Srednio traci": f"{statistics['average_goals_against']:.2f}",
            }
        )
    return rows


def request_match_prediction(api_url: str, prediction_request: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{api_url}/predict", json=prediction_request, timeout=60)
    response.raise_for_status()
    return response.json()


def get_error_message_from_response(response: requests.Response | None) -> str:
    if response is None:
        return "API zwrocilo blad bez odpowiedzi."

    try:
        response_body = response.json()
    except ValueError:
        return response.text

    return response_body.get("detail", response.text)


if __name__ == "__main__":
    main()
