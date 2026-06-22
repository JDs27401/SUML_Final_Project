@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Nie znaleziono interpretera: "%PYTHON_EXE%"
    exit /b 1
)

cd /d "%PROJECT_ROOT%"
"%PYTHON_EXE%" -m uvicorn App.api:app --host 127.0.0.1 --port 8000 --reload
