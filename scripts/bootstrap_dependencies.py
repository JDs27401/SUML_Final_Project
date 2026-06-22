from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


MINIMUM_PYTHON_VERSION = (3, 14)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE_PATH = PROJECT_ROOT / "requirements.txt"
REQUIRED_IMPORTS = {
    "pandas": "pandas",
    "scikit-learn": "sklearn",
    "joblib": "joblib",
    "streamlit": "streamlit",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "requests": "requests",
}


def main() -> None:
    stop_when_python_version_is_not_supported()
    missing_packages = get_missing_packages()

    if not missing_packages:
        print("Wszystkie wymagane biblioteki sa juz zainstalowane.")
        return

    print("Brakujace biblioteki: " + ", ".join(missing_packages))
    install_requirements()


def stop_when_python_version_is_not_supported() -> None:
    if sys.version_info >= MINIMUM_PYTHON_VERSION:
        return

    raise SystemExit(
        "Aplikacja wymaga Python 3.14. Ustaw interpreter projektu na .venv\\Scripts\\python.exe."
    )


def get_missing_packages() -> list[str]:
    return [
        package_name
        for package_name, import_name in REQUIRED_IMPORTS.items()
        if importlib.util.find_spec(import_name) is None
    ]


def install_requirements() -> None:
    if not REQUIREMENTS_FILE_PATH.exists():
        raise SystemExit(f"Nie znaleziono pliku: {REQUIREMENTS_FILE_PATH}")

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE_PATH),
        ],
        cwd=PROJECT_ROOT,
    )


if __name__ == "__main__":
    main()
