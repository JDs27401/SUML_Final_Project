# SUML_Final_Project

Aplikacja Streamlit przewidujaca wynik meczu pilkarskiego na podstawie regresji liniowej.

## Uruchomienie calej aplikacji

# run_app.bat - uruchamia backend jak i front end

## Uruchamianie frontend'u

# run_streamlit.bat

## Uruchamianie tylko backend'u

# run_api.bat

Endpointy API:

- `GET /health`
- `GET /metadata`
- `POST /predict`
- `POST /retrain`

Model trenuje sie automatycznie przy pierwszym uruchomieniu i zapisuje artefakt w `Model/artifacts`.
