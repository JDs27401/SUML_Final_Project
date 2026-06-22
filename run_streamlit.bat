@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
call scripts\ensure_environment.bat "%PROJECT_ROOT%"
if errorlevel 1 exit /b 1

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
"%PYTHON_EXE%" scripts\bootstrap_dependencies.py
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -m streamlit run App\app.py
