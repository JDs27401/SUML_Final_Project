# SUML_Final_Project

# Aplikacja Streamlit przewidujaca wynik meczu pilkarskiego na podstawie regresji liniowej.
## Działanie aplikacji opiera się na wybraniu drużyn A i B
## Następnie należy wybrać która drużyna jest drużyną gospodarzy, a w przypadku turniejów albo braku gospodarza można wybrać opcję bez
## Forma meczu, np.: Friendly albo FIFA World Cup, określa typ rozgrywek 

## Uruchomienie calej aplikacji

```run_app.bat - uruchamia backend jak i front end```

# Uruchamianie frontend'u

```run_streamlit.bat```

# Uruchamianie tylko backend'u

```run_api.bat```

Endpointy API:

- `GET /health`
- `GET /metadata`
- `POST /predict`
- `POST /retrain`

Model trenuje sie automatycznie przy pierwszym uruchomieniu i zapisuje artefakt w `Model/artifacts`.
