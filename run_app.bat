@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
call scripts\ensure_environment.bat "%PROJECT_ROOT%"
if errorlevel 1 exit /b 1

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
"%PYTHON_EXE%" scripts\bootstrap_dependencies.py
if errorlevel 1 exit /b 1

start "Football Predictor API" "%PYTHON_EXE%" -m uvicorn App.api:app --host 127.0.0.1 --port 8000
timeout /t 5 /nobreak > nul
"%PYTHON_EXE%" -m streamlit run App\app.py
