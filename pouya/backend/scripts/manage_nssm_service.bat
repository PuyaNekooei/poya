@echo off
title Django Backend Service Manager (NSSM)
echo Django Restaurant Backend Service Manager
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

:menu
echo.
echo Choose an option:
echo 1. Start service
echo 2. Stop service
echo 3. Restart service
echo 4. Check status
echo 5. View logs
echo 6. Configure service
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto configure
if "%choice%"=="7" goto exit
echo Invalid choice. Please try again.
goto menu

:start
echo.
echo Starting service...
nssm start DjangoRestaurantBackend
if %errorLevel% == 0 (
    echo Service started successfully!
) else (
    echo Failed to start service!
)
goto menu

:stop
echo.
echo Stopping service...
nssm stop DjangoRestaurantBackend
if %errorLevel% == 0 (
    echo Service stopped successfully!
) else (
    echo Failed to stop service!
)
goto menu

:restart
echo.
echo Restarting service...
nssm stop DjangoRestaurantBackend
timeout /t 2 /nobreak >nul
nssm start DjangoRestaurantBackend
if %errorLevel% == 0 (
    echo Service restarted successfully!
) else (
    echo Failed to restart service!
)
goto menu

:status
echo.
echo Service status:
nssm status DjangoRestaurantBackend
echo.
echo Windows service status:
sc query DjangoRestaurantBackend
goto menu

:logs
echo.
echo Recent service logs:
echo ===================
if exist "service.log" (
    echo.
    echo Service Log (last 20 lines):
    echo -----------------------------
    powershell "Get-Content 'service.log' -Tail 20"
) else (
    echo No service log found.
)

if exist "service_error.log" (
    echo.
    echo Error Log (last 20 lines):
    echo ---------------------------
    powershell "Get-Content 'service_error.log' -Tail 20"
) else (
    echo No error log found.
)
goto menu

:configure
echo.
echo Opening NSSM configuration...
nssm edit DjangoRestaurantBackend
goto menu

:exit
echo.
echo Goodbye!
pause

