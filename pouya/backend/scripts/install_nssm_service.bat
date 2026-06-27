@echo off
title Django Backend Service Installer (NSSM)
echo Installing Django Restaurant Backend using NSSM...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
) else (
    echo ERROR: This script must be run as Administrator!
    echo Right-click on this file and select "Run as administrator"
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Change to backend directory (scripts live in backend\scripts)
cd /d "%~dp0.."
echo Current directory: %CD%

REM Check if NSSM is available
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo NSSM not found. Downloading NSSM...
    echo.
    
    REM Create temp directory
    if not exist "temp" mkdir temp
    cd temp
    
    REM Download NSSM (you can also download manually from https://nssm.cc/download)
    echo Please download NSSM from https://nssm.cc/download
    echo Extract nssm.exe to this directory: %CD%
    echo Then run this script again.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo NSSM found. Proceeding with service installation...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found.
    set PYTHON_EXE=%CD%\venv\Scripts\python.exe
    echo Using Python: %PYTHON_EXE%
) else (
    echo Virtual environment not found. Using system Python.
    set PYTHON_EXE=python
    echo Using Python: %PYTHON_EXE%
)

echo.

REM Stop and remove existing service if it exists
echo Stopping existing service...
nssm stop DjangoRestaurantBackend
nssm remove DjangoRestaurantBackend confirm

echo.

REM Install the service
echo Installing Django Backend Service...
nssm install DjangoRestaurantBackend "%PYTHON_EXE%" "manage.py runserver 0.0.0.0:8000"

if %errorLevel% neq 0 (
    echo ERROR: Failed to install service!
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Service installed successfully!
echo.

REM Configure the service
echo Configuring service...
nssm set DjangoRestaurantBackend AppDirectory "%CD%"
nssm set DjangoRestaurantBackend DisplayName "Django Restaurant Backend Service"
nssm set DjangoRestaurantBackend Description "Runs the Django restaurant backend server as a Windows service"
nssm set DjangoRestaurantBackend Start SERVICE_AUTO_START

REM Set environment variables
nssm set DjangoRestaurantBackend AppEnvironmentExtra "DJANGO_SETTINGS_MODULE=restaurant_backend.settings"

REM Configure logging
nssm set DjangoRestaurantBackend AppStdout "%CD%\service.log"
nssm set DjangoRestaurantBackend AppStderr "%CD%\service_error.log"

REM Set service to restart on failure
nssm set DjangoRestaurantBackend AppExit Default Restart
nssm set DjangoRestaurantBackend AppRestartDelay 5000

echo Service configured successfully!
echo.

REM Start the service
echo Starting service...
nssm start DjangoRestaurantBackend

if %errorLevel% == 0 (
    echo.
    echo Service started successfully!
    echo.
    echo Service Details:
    echo - Name: DjangoRestaurantBackend
    echo - Display Name: Django Restaurant Backend Service
    echo - Status: Running
    echo - Django Server: http://localhost:8000
    echo - Log File: %CD%\service.log
    echo - Error Log: %CD%\service_error.log
    echo.
    echo You can manage the service using:
    echo - Services.msc (Windows Services Manager)
    echo - nssm commands
    echo - manage_nssm_service.bat
    echo.
) else (
    echo ERROR: Failed to start the service!
    echo Check the error log: %CD%\service_error.log
    echo.
)

echo.
echo Press any key to exit...
pause >nul

