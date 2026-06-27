# PowerShell script to start the Restaurant Management System
# Run from the app root (scripts live under the app root)
Set-Location (Join-Path $PSScriptRoot '..')
Write-Host "Starting Restaurant Management System..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if backend directory exists
if (-not (Test-Path "..\backend")) {
    Write-Host "ERROR: Backend directory not found!" -ForegroundColor Red
    Write-Host "Please make sure the Django backend is in the correct location." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if frontend is built
if (-not (Test-Path "frontend\dist")) {
    Write-Host "Frontend not built. Building now..." -ForegroundColor Yellow
    Set-Location "frontend"
    npm install
    npm run build
    Set-Location ".."
}

# Start Django Backend Server
Write-Host "Starting Django Backend Server..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c", "cd ..\backend && python manage.py runserver 8000" -WindowStyle Normal -PassThru

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create virtual environment first: python -m venv venv" -ForegroundColor Red
    Write-Host "Then install dependencies: venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start PyWebView Application
Write-Host "Starting PyWebView Application..." -ForegroundColor Yellow
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & "venv\Scripts\Activate.ps1"
    python main.py
} catch {
    Write-Host "Error starting PyWebView application: $_" -ForegroundColor Red
}

# Cleanup - stop backend server when PyWebView closes
Write-Host "Stopping backend server..." -ForegroundColor Yellow
if ($backendProcess -and !$backendProcess.HasExited) {
    $backendProcess.Kill()
}

Write-Host "Application closed." -ForegroundColor Green
Read-Host "Press Enter to exit"
