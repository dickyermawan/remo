@echo off
:: REMO - Start Bot (Background - No Console)

cd /d "%~dp0"

:: Check .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

:: Create logs directory
if not exist "logs" mkdir "logs"

echo Starting REMO bot in background (no console)...
echo.

:: Launch .pyw file (Windows will use pythonw.exe automatically)
start "" "main.pyw"

:: Wait for startup
timeout /t 5 /nobreak >nul

:: Check if running
curl -s http://localhost:8443/health >nul 2>&1

if %errorLevel% == 0 (
    echo ========================================
    echo REMO Bot Started Successfully!
    echo ========================================
    echo.
    echo Status: Running in background (no console)
    echo Dashboard: http://localhost:8443/
    echo Logs: logs\remo.log
    echo.
    echo Process: pythonw.exe (check Task Manager)
    echo To stop: run stop.bat
    echo.
) else (
    echo ========================================  
    echo Bot started, waiting for initialization...
    echo ========================================
    echo.
    echo Wait 10 more seconds then check:
    echo - Dashboard: http://localhost:8443/
    echo - Logs: logs\remo.log
    echo - Task Manager for pythonw.exe
    echo.
)

pause
