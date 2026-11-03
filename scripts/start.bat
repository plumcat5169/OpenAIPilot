@echo off
SET "VENV_DIR=venv"

IF NOT EXIST "%VENV_DIR%" (
    echo Virtual environment not found. Run install_deps.bat first.
    pause
    exit /b 1
)

CALL "%VENV_DIR%\Scripts\activate"

cd /d "%~dp0.."
python -m OpenAIPilot.main
pause
