@echo off
setlocal

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%~dp0..\"

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    exit /b 0
)

echo Nie znaleziono lokalnego srodowiska .venv. Tworze .venv dla projektu...

where py > nul 2>&1
if not errorlevel 1 (
    py -3.14 -c "import sys" > nul 2>&1
    if not errorlevel 1 (
        py -3.14 -m venv "%PROJECT_ROOT%.venv"
        exit /b %errorlevel%
    )
)

where python > nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 14) else 1)" > nul 2>&1
    if not errorlevel 1 (
        python -m venv "%PROJECT_ROOT%.venv"
        exit /b %errorlevel%
    )
)

echo Nie znaleziono zainstalowanego Python 3.14.
echo Zainstaluj Python 3.14 i uruchom ponownie ten skrypt.
exit /b 1
