# SUML_Final_Project

Aplikacja Streamlit przewidujaca wynik meczu pilkarskiego na podstawie regresji liniowej.

## Uruchomienie calej aplikacji

Backend API startuje na `http://127.0.0.1:8000`, a frontend Streamlit na adresie pokazanym w terminalu.

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run_app.bat
```

Mozesz tez uruchomic warstwy osobno:

```powershell
.\run_api.bat
.\run_streamlit.bat
```

Endpointy API:

- `GET /health`
- `GET /metadata`
- `POST /predict`
- `POST /retrain`

Model trenuje sie automatycznie przy pierwszym uruchomieniu i zapisuje artefakt w `Model/artifacts`.

Projekt jest skonfigurowany pod Python 3.14.6. W PyCharm ustaw interpreter:

```text
C:\Users\djdom\Desktop\Pyton\SUML\SUML_Final_Project\.venv\Scripts\python.exe
```
