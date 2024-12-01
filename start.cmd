@echo off

echo.
echo Starting the app...
echo.
cd src
start http://127.0.0.1:5000
set FLASK_APP=api:app
call python -m flask run --port 5000 --reload
if "%errorlevel%" neq "0" (
    echo Failed to start the app.
    exit /B %errorlevel%
)