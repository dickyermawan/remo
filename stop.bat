@echo off
:: REMO - Stop Bot

echo Stopping REMO bot...

:: Kill python processes running main.py
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *main.py*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq *main.py*" /F >nul 2>&1

:: Also try to kill by port (more reliable)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8443" ^| find "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
    echo Stopped process using port 8443 (PID: %%a)
)

echo.
echo REMO bot stopped!
echo.
pause
