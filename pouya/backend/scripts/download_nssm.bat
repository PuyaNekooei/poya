@echo off
title NSSM Downloader
echo Downloading NSSM (Non-Sucking Service Manager)...
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

REM Create temp directory
if not exist "temp" mkdir temp
cd temp

echo Downloading NSSM...
echo.

REM Try to download NSSM using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'}"

if %errorLevel% == 0 (
    echo Download successful!
    echo.
    echo Extracting NSSM...
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.' -Force"
    
    echo.
    echo Copying NSSM to backend directory...
    copy "nssm-2.24\win64\nssm.exe" "..\nssm.exe"
    
    if %errorLevel% == 0 (
        echo.
        echo NSSM installed successfully!
        echo You can now run the service installation scripts.
        echo.
        echo Files created:
        echo - nssm.exe (in backend directory)
        echo.
    ) else (
        echo ERROR: Failed to copy NSSM executable!
    )
) else (
    echo ERROR: Failed to download NSSM!
    echo.
    echo Please download NSSM manually:
    echo 1. Go to https://nssm.cc/download
    echo 2. Download nssm-2.24.zip
    echo 3. Extract nssm.exe to this directory: %CD%
    echo 4. Run the service installation scripts
    echo.
)

echo.
echo Press any key to exit...
pause >nul

