@echo off
:: REMO - Install as Windows Service
:: Run this script as Administrator

echo ========================================
echo REMO - Install Windows Service
echo ========================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator
    pause
    exit /b 1
)

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0

:: Find Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo Found Python: %PYTHON_PATH%

:: Check if NSSM exists
if not exist "%SCRIPT_DIR%nssm.exe" (
    echo.
    echo NSSM not found. Downloading...
    echo Please download NSSM from https://nssm.cc/download
    echo and place nssm.exe in: %SCRIPT_DIR%
    echo.
    echo Or install via Chocolatey: choco install nssm
    pause
    exit /b 1
)

:: Stop existing service if running
echo.
echo Stopping existing REMO service if running...
nssm stop REMO >nul 2>&1
nssm remove REMO confirm >nul 2>&1

:: Install the service
echo.
echo Installing REMO service...
"%SCRIPT_DIR%nssm.exe" install REMO "%PYTHON_PATH%" "%SCRIPT_DIR%main.py"

:: Configure service
echo Configuring service...
"%SCRIPT_DIR%nssm.exe" set REMO AppDirectory "%SCRIPT_DIR%"
"%SCRIPT_DIR%nssm.exe" set REMO DisplayName "REMO - Remote Control Bot"
"%SCRIPT_DIR%nssm.exe" set REMO Description "Telegram bot for remote laptop control"
"%SCRIPT_DIR%nssm.exe" set REMO Start SERVICE_AUTO_START
"%SCRIPT_DIR%nssm.exe" set REMO AppStdout "%SCRIPT_DIR%logs\service_stdout.log"
"%SCRIPT_DIR%nssm.exe" set REMO AppStderr "%SCRIPT_DIR%logs\service_stderr.log"
"%SCRIPT_DIR%nssm.exe" set REMO AppRotateFiles 1
"%SCRIPT_DIR%nssm.exe" set REMO AppRotateBytes 10485760

:: Create logs directory
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

:: Start the service
echo.
echo Starting REMO service...
"%SCRIPT_DIR%nssm.exe" start REMO

echo.
echo ========================================
echo REMO service installed and started!
echo ========================================
echo.
echo Service Name: REMO
echo Status: Check with 'nssm status REMO'
echo Logs: %SCRIPT_DIR%logs\
echo.
echo To uninstall: nssm remove REMO confirm
echo.
pause
