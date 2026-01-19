@echo off
:: REMO - One-Click Install as Windows Service
:: Auto-downloads NSSM and installs service
:: Run this script as Administrator

echo ========================================
echo REMO - One-Click Service Installer
echo ========================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator
    echo Right-click and select "Run as Administrator"
    pause
    exit /b 1
)

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Find Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo [OK] Found Python: %PYTHON_PATH%

:: Check if .env exists
if not exist "%SCRIPT_DIR%.env" (
    echo.
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it first.
    echo.
    pause
    exit /b 1
)

:: Create logs directory
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

:: Download NSSM if not present
if not exist "%SCRIPT_DIR%nssm.exe" (
    echo.
    echo NSSM not found. Downloading from GitHub...
    echo.
    
    :: Use PowerShell to download NSSM
    powershell -Command "& { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/kirillkovalenko/nssm/releases/download/2.24-101-g897c7ad/nssm-2.24-101-g897c7ad.zip' -OutFile '%SCRIPT_DIR%nssm.zip' }"
    
    if not exist "%SCRIPT_DIR%nssm.zip" (
        echo ERROR: Failed to download NSSM
        echo.
        echo Please download manually from:
        echo https://github.com/kirillkovalenko/nssm/releases
        echo And extract nssm.exe to: %SCRIPT_DIR%
        pause
        exit /b 1
    )
    
    echo Extracting NSSM...
    powershell -Command "& { Expand-Archive -Path '%SCRIPT_DIR%nssm.zip' -DestinationPath '%SCRIPT_DIR%nssm_temp' -Force }"
    
    :: Find nssm.exe in extracted folder (x64 version)
    for /r "%SCRIPT_DIR%nssm_temp" %%f in (nssm.exe) do (
        if exist "%%f" (
            echo %%f | findstr /i "win64" >nul
            if not errorlevel 1 (
                copy "%%f" "%SCRIPT_DIR%nssm.exe" >nul
            )
        )
    )
    
    :: Cleanup
    del "%SCRIPT_DIR%nssm.zip" >nul 2>&1
    rmdir /s /q "%SCRIPT_DIR%nssm_temp" >nul 2>&1
    
    if not exist "%SCRIPT_DIR%nssm.exe" (
        echo ERROR: Failed to extract NSSM
        pause
        exit /b 1
    )
    
    echo [OK] NSSM downloaded successfully!
)

echo [OK] NSSM ready

:: Stop existing service if running
echo.
echo Checking for existing REMO service...
nssm stop REMO >nul 2>&1
nssm remove REMO confirm >nul 2>&1
echo [OK] Existing service removed (if any)

:: Install the service
echo.
echo Installing REMO service...
"%SCRIPT_DIR%nssm.exe" install REMO "%PYTHON_PATH%" "%SCRIPT_DIR%main.py"

if %errorLevel% neq 0 (
    echo ERROR: Failed to install service
    pause
    exit /b 1
)

:: Configure service
echo Configuring service...
"%SCRIPT_DIR%nssm.exe" set REMO AppDirectory "%SCRIPT_DIR%"
"%SCRIPT_DIR%nssm.exe" set REMO DisplayName "REMO - Remote Control Bot"
"%SCRIPT_DIR%nssm.exe" set REMO Description "Telegram bot for remote laptop control via webhook"
"%SCRIPT_DIR%nssm.exe" set REMO Start SERVICE_AUTO_START
"%SCRIPT_DIR%nssm.exe" set REMO AppStdout "%SCRIPT_DIR%logs\service_stdout.log"
"%SCRIPT_DIR%nssm.exe" set REMO AppStderr "%SCRIPT_DIR%logs\service_stderr.log"
"%SCRIPT_DIR%nssm.exe" set REMO AppRotateFiles 1
"%SCRIPT_DIR%nssm.exe" set REMO AppRotateBytes 10485760
echo [OK] Service configured

:: Start the service
echo.
echo Starting REMO service...
"%SCRIPT_DIR%nssm.exe" start REMO

if %errorLevel% neq 0 (
    echo ERROR: Failed to start service
    echo Check logs in: %SCRIPT_DIR%logs\
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! REMO service installed!
echo ========================================
echo.
echo Service Name: REMO
echo Status: Running
echo Auto-start: Enabled
echo Logs: %SCRIPT_DIR%logs\
echo.
echo Dashboard: http://localhost:8443/
echo.
echo Commands:
echo - Check status: nssm status REMO
echo - Stop service: nssm stop REMO
echo - Start service: nssm start REMO
echo - Uninstall: run uninstall_service.bat
echo.
pause
