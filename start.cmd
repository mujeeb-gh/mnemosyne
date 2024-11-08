@echo off

echo.
echo Starting the app...
echo.
cd src
call python api.py
if "%errorlevel%" neq "0" (
    echo Failed to start the app.
    exit /B %errorlevel%
)