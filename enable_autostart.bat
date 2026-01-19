@echo off
:: REMO - Setup Auto-Start on Windows Boot
:: Creates Task Scheduler entry to auto-start REMO

echo ========================================
echo REMO - Setup Auto-Start
echo ========================================
echo.

:: Check for admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
set TASK_NAME=REMO Bot Auto-Start

:: Remove existing task if present
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Create new task
echo Creating auto-start task...
schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_DIR%start.bat\"" /sc onlogon /rl highest /f

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo Auto-Start Configured Successfully!
    echo ========================================
    echo.
    echo Task Name: %TASK_NAME%
    echo Trigger: On Windows Logon
    echo.
    echo REMO will now auto-start when you log in to Windows!
    echo.
    echo To disable: run disable_autostart.bat
    echo.
) else (
    echo ERROR: Failed to create task
)

pause
