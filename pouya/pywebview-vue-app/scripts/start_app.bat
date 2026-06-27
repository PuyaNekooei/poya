@echo off
REM Run from the app root (scripts live under the app root)
cd /d "%~dp0.."
echo Starting Restaurant Management System...
echo =====================================

@REM REM Check if backend directory exists
@REM if not exist "..\backend" (
@REM     echo ERROR: Backend directory not found!
@REM     echo Please make sure the Django backend is in the correct location.
@REM     pause
@REM     exit /b 1
@REM )

REM Check if frontend is built
if not exist "frontend\dist" (
    echo Frontend not built. Building now...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

@REM echo Starting Django Backend Server...
@REM start "Django Backend" cmd /c "cd ..\backend && python manage.py runserver 8000"

@REM REM Wait a moment for backend to start
@REM timeout /t 3 /nobreak > nul

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create virtual environment first: python -m venv venv
    echo Then install dependencies: venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting PyWebView Application...
echo Activating virtual environment...
call venv\Scripts\activate.bat
python main.py

echo.
echo Application closed.
pause
