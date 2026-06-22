# SUML_Final_Project

Aplikacja przewiduje wynik meczu pilkarskiego na podstawie regresji liniowej.

Architektura:
- FastAPI udostepnia backend API.
- Streamlit udostepnia frontend.
- Warstwy `Data` i `Model` odpowiadaja za dane, cechy i predykcje.

## Jak dziala aplikacja

1. Wybierasz dwie druzyny.
2. Wybierasz, ktora druzyna jest gospodarzem, albo opcje boiska neutralnego.
3. Wybierasz turniej, kraj rozegrania meczu i date meczu.
4. Aplikacja zwraca predykcje, przyblizony wynik, szacowane gole i statystyki formy druzyn.

## Uruchomienie calej aplikacji

```powershell
.\run_app.bat
```

`run_app.bat` uruchamia backend i frontend. Przy pierwszym starcie:
- tworzy lokalne `.venv`, jesli go nie ma,
- instaluje brakujace biblioteki z `requirements.txt`,
- uruchamia API na `http://127.0.0.1:8000`,
- uruchamia frontend Streamlit.

Do utworzenia `.venv` potrzebny jest zainstalowany Python 3.14 dostepny jako `py -3.14` albo `python`.

## Uruchamianie warstw osobno

Backend:

```powershell
.\run_api.bat
```

Frontend:

```powershell
.\run_streamlit.bat
```

## Endpointy API

- `GET /health`
- `GET /metadata`
- `POST /predict`
- `POST /retrain`

Dokumentacja API po uruchomieniu backendu:

```text
http://127.0.0.1:8000/docs
```

Model trenuje sie automatycznie przy pierwszym uruchomieniu i zapisuje artefakt w `Model/artifacts`.
