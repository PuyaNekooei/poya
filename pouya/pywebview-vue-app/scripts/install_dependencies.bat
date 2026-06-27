@echo off
REM Run from the app root (scripts live under the app root)
cd /d "%~dp0.."
echo Installing PyWebView Application Dependencies...
echo ==============================================

REM Install Python packages
echo Installing Python packages...
pip install jdatetime==5.0.0
pip install python-bidi==0.6.6
pip install arabic-reshaper==3.0.0
pip install pywebview==5.0.7
pip install Pillow==10.4.0
pip install pywin32==306
pip install requests==2.31.0

echo.
echo Installing frontend dependencies...
cd frontend
call npm install
call npm run build
cd ..

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo 1. Start Django backend: cd ..\backend && python manage.py runserver 8000
echo 2. Start PyWebView app: python main.py
echo.
pause
