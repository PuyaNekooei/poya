@echo off
title Django Backend Service Uninstaller (NSSM)
echo Uninstalling Django Restaurant Backend Service...
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

REM Check if NSSM is available
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: NSSM not found!
    echo Please make sure NSSM is installed and in your PATH.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.

REM Stop the service
echo Stopping service...
nssm stop DjangoRestaurantBackend

REM Remove the service
echo Removing service...
nssm remove DjangoRestaurantBackend confirm

if %errorLevel% == 0 (
    echo.
    echo Service uninstalled successfully!
    echo The Django backend is no longer running as a Windows service.
) else (
    echo ERROR: Failed to uninstall the service!
    echo The service may not be installed or you may not have sufficient privileges.
)

echo.
echo Press any key to exit...
pause >nul

