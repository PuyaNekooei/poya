# Django Restaurant Backend - Windows Service Setup (NSSM)

This guide explains how to set up your Django restaurant backend as a Windows service using NSSM (Non-Sucking Service Manager) that starts automatically when the computer boots up.

## Overview

The Windows service setup uses NSSM:

### Django Backend Service
- **Service Name**: `DjangoRestaurantBackend`
- **Display Name**: `Django Restaurant Backend Service`
- **Django Server**: http://localhost:8000
- **Auto-start**: Yes (starts when Windows boots)

## Files Created

### NSSM-Based Service Files
1. **`download_nssm.bat`** - Downloads and installs NSSM
2. **`install_nssm_service.bat`** - Installs Django backend service using NSSM
3. **`uninstall_nssm_service.bat`** - Uninstalls Django backend service
4. **`manage_nssm_service.bat`** - Service management script with menu
5. **`nssm.exe`** - NSSM executable (downloaded automatically)
6. **`service.log`** - Django service log file (created automatically)

## Quick Setup

### Method 1: Using NSSM Batch Scripts (Recommended)

#### Step 1: Download and Install NSSM

1. **Download NSSM:**
   - Right-click on `download_nssm.bat`
   - Select "Run as administrator"
   - This will automatically download and install NSSM

#### Step 2: Install Django Backend Service

1. **Install Django service:**
   - Right-click on `install_nssm_service.bat`
   - Select "Run as administrator"
   - Follow the on-screen instructions

2. **Uninstall Django service:**
   - Right-click on `uninstall_nssm_service.bat`
   - Select "Run as administrator"

### Method 2: Using PowerShell Script

1. **Open PowerShell as Administrator**
2. **Navigate to the backend directory:**
   ```powershell
   cd "D:\Projects\yas\backend"
   ```

3. **Run the management script:**
   
   ```powershell
   # Install service
   .\manage_service.ps1 -Action install
   
   # Check status
   .\manage_service.ps1 -Action status
   
   # View logs
   .\manage_service.ps1 -Action logs
   
   # Stop service
   .\manage_service.ps1 -Action stop
   
   # Start service
   .\manage_service.ps1 -Action start
   
   # Restart service
   .\manage_service.ps1 -Action restart
   
   # Uninstall service
   .\manage_service.ps1 -Action uninstall
   ```

## Manual Installation

If you prefer to install manually:

1. **Install dependencies:**
   ```bash
   pip install pywin32
   ```

2. **Install the service:**
   ```bash
   python windows_service.py install
   ```

3. **Start the service:**
   ```bash
   python windows_service.py start
   ```

## Service Management

### Using Windows Services Manager

1. Press `Win + R`, type `services.msc`, and press Enter
2. Find "Django Restaurant Backend Service"
3. Right-click to start, stop, or configure the service

### Using Command Line

```bash
# Start service
python windows_service.py start

# Stop service
python windows_service.py stop

# Restart service
python windows_service.py stop
python windows_service.py start

# Remove service
python windows_service.py remove
```

### Using PowerShell

```powershell
# Check service status
Get-Service -Name "DjangoRestaurantBackend"

# Start service
Start-Service -Name "DjangoRestaurantBackend"

# Stop service
Stop-Service -Name "DjangoRestaurantBackend"

# Restart service
Restart-Service -Name "DjangoRestaurantBackend"
```

## Configuration

### Service Settings

The service is configured with:
- **Startup Type**: Automatic (starts with Windows)
- **Log On**: Local System account
- **Recovery**: Restart on failure

### Port Configuration

The Django server runs on port 8000 by default. To change this:

1. Edit `windows_service.py`
2. Find the line: `'0.0.0.0:8000'`
3. Change to your desired port
4. Reinstall the service

### Virtual Environment

The service automatically detects and uses your virtual environment if it exists at `backend/venv/`. If no virtual environment is found, it uses the system Python.

## Troubleshooting

### Common Issues

1. **"Access Denied" Error:**
   - Make sure you're running as Administrator
   - Check that the service isn't already installed

2. **Service Won't Start:**
   - Check the `service.log` file for error details
   - Verify that all dependencies are installed
   - Ensure port 8000 is not in use by another application

3. **Service Stops Unexpectedly:**
   - Check the Windows Event Viewer for system errors
   - Review the `service.log` file
   - Verify database connectivity

### Log Files

- **Service Log**: `backend/service.log`
- **Windows Event Log**: Event Viewer → Windows Logs → Application

### Testing the Service

1. **Check if service is running:**
   ```bash
   netstat -an | findstr :8000
   ```

2. **Test the API:**
   ```bash
   curl http://localhost:8000/api/
   ```

3. **View service status:**
   ```powershell
   Get-Service -Name "DjangoRestaurantBackend"
   ```

## Security Considerations

- The service runs under the Local System account
- Ensure your Django settings are secure for production use
- Consider using environment variables for sensitive configuration
- Regularly update dependencies for security patches

## Production Recommendations

For production deployment:

1. **Use a production WSGI server** (like Gunicorn or uWSGI) instead of Django's development server
2. **Configure proper logging** with log rotation
3. **Set up monitoring** and health checks
4. **Use environment variables** for configuration
5. **Enable HTTPS** with proper SSL certificates
6. **Configure firewall rules** appropriately

## Support

If you encounter issues:

1. Check the `service.log` file
2. Review Windows Event Viewer logs
3. Verify all dependencies are installed
4. Ensure proper permissions are set
5. Test the Django application manually first

---

**Note**: This setup is designed for development and testing. For production use, consider using a proper WSGI server and reverse proxy setup.
