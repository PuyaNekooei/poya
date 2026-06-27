@echo off
REM ============================================================
REM  Launch the Django backend using its OWN venv
REM ============================================================
setlocal
set "PROJECT_DIR=%~dp0backend"
set "VENV_PY=%PROJECT_DIR%\venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [ERROR] Backend venv not found at: %VENV_PY%
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
echo Starting Django backend on http://localhost:8000 ...
"%VENV_PY%" manage.py runserver 0.0.0.0:4040

echo.
echo Server stopped.
pause
endlocal
