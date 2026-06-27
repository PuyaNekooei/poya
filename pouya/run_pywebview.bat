@echo off
REM ============================================================
REM  Launch the pywebview Vue app using its OWN venv
REM ============================================================
setlocal
set "PROJECT_DIR=%~dp0pywebview-vue-app"
set "VENV_PY=%PROJECT_DIR%\venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [ERROR] pywebview venv not found at: %VENV_PY%
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
echo Starting pywebview app ...
"%VENV_PY%" main.py

echo.
echo App closed.
pause
endlocal
