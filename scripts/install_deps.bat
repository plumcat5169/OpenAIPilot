@echo off
SET "PROJECT_ROOT=%~dp0.."
SET "VENV_DIR=%PROJECT_ROOT%\venv"

IF NOT EXIST "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

cd /d "%PROJECT_ROOT%"

echo Upgrading pip...
"%VENV_DIR%\Scripts\python" -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
"%VENV_DIR%\Scripts\pip" install -r requirements.txt

echo Dependencies installed successfully.
pause