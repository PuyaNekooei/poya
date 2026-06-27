@echo off
REM Run from the app root (scripts live under the app root)
cd /d "%~dp0.."
echo Downloading Vazir Font Files...
echo =================================

cd frontend\src\assets\fonts

echo Downloading Vazir Regular...
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/vazir-font@30.1.0/dist/Vazir-Regular.ttf' -OutFile 'Vazir-Regular.ttf'"

echo Downloading Vazir Bold...
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/vazir-font@30.1.0/dist/Vazir-Bold.ttf' -OutFile 'Vazir-Bold.ttf'"

echo Downloading Vazir Medium...
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/vazir-font@30.1.0/dist/Vazir-Medium.ttf' -OutFile 'Vazir-Medium.ttf'"

echo Downloading Vazir Light...
powershell -Command "Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/vazir-font@30.1.0/dist/Vazir-Light.ttf' -OutFile 'Vazir-Light.ttf'"

cd ..\..\..\..

echo.
echo ========================================
echo Vazir fonts downloaded successfully!
echo ========================================
echo.
pause


