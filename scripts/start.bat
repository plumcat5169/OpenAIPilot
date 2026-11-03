@echo off
SET "PROJECT_ROOT=%~dp0.."
SET "VENV_DIR=%PROJECT_ROOT%\venv"

IF NOT EXIST "%VENV_DIR%" (
    echo Virtual environment not found. Run install_deps.bat first.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%"
"%VENV_DIR%\Scripts\python.exe" -m OpenAIPilot.main

pause