@echo off
:: REMO - Disable Auto-Start

echo ========================================
echo REMO - Disable Auto-Start
echo ========================================
echo.

:: Check for admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator
    pause
    exit /b 1
)

set TASK_NAME=REMO Bot Auto-Start

:: Remove task
echo Removing auto-start task...
schtasks /delete /tn "%TASK_NAME%" /f

if %errorLevel% == 0 (
    echo.
    echo Auto-Start Disabled!
    echo.
    echo REMO will no longer start automatically.
    echo Use start.bat to start manually.
    echo.
) else (
    echo Task not found or already disabled.
)

pause
