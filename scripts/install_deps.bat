@echo off
SET "VENV_DIR=venv"

IF NOT EXIST "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

CALL "%VENV_DIR%\Scripts\activate"

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
cd /d "%~dp0.."
pip install -r requirements.txt

echo Dependencies installed successfully.
pause
