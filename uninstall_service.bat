@echo off
:: REMO - Uninstall Windows Service
:: Run this script as Administrator

echo ========================================
echo REMO - Uninstall Windows Service
echo ========================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0

:: Stop and remove service
echo Stopping REMO service...
"%SCRIPT_DIR%nssm.exe" stop REMO >nul 2>&1

echo Removing REMO service...
"%SCRIPT_DIR%nssm.exe" remove REMO confirm

echo.
echo ========================================
echo REMO service uninstalled!
echo ========================================
pause
