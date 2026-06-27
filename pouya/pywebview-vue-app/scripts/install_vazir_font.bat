@echo off
REM Run from the app root (scripts live under the app root)
cd /d "%~dp0.."
echo Installing Vazir Font for Persian Support...
echo ==========================================

REM Check if PowerShell is available
powershell -Command "Get-Command Invoke-WebRequest" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell with web support not available
    echo Please download Vazir font manually from: https://github.com/rastikerdar/vazir-font
    pause
    exit /b 1
)

REM Create temp directory
if not exist "temp" mkdir temp

echo Downloading Vazir Font...
powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/rastikerdar/vazir-font/releases/download/v30.1.0/vazir-font-v30.1.0.zip' -OutFile 'temp\vazir-font.zip' } catch { Write-Host 'Download failed'; exit 1 }"

if not exist "temp\vazir-font.zip" (
    echo ERROR: Failed to download Vazir font
    echo Please download manually from: https://github.com/rastikerdar/vazir-font
    pause
    exit /b 1
)

echo Extracting font files...
powershell -Command "Expand-Archive -Path 'temp\vazir-font.zip' -DestinationPath 'temp\vazir' -Force"

echo Installing fonts...
if exist "temp\vazir\vazir-font-v30.1.0\ttf\Vazir-Bold.ttf" (
    copy "temp\vazir\vazir-font-v30.1.0\ttf\Vazir-Bold.ttf" "%WINDIR%\Fonts\"
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Vazir Bold (TrueType)" /t REG_SZ /d "Vazir-Bold.ttf" /f >nul 2>&1
    echo ✅ Vazir Bold installed
)

if exist "temp\vazir\vazir-font-v30.1.0\ttf\Vazir.ttf" (
    copy "temp\vazir\vazir-font-v30.1.0\ttf\Vazir.ttf" "%WINDIR%\Fonts\"
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Vazir (TrueType)" /t REG_SZ /d "Vazir.ttf" /f >nul 2>&1
    echo ✅ Vazir Regular installed
)

REM Cleanup
echo Cleaning up temporary files...
rmdir /s /q temp >nul 2>&1

echo.
echo ========================================
echo Vazir Font installation completed!
echo ========================================
echo.
echo Note: You may need to restart the application
echo to see the new font in use.
echo.
pause


