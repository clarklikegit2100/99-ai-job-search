@echo off
setlocal

rem Always run from the directory containing this script.
cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker was not found. Install and start Docker Desktop first.
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running. Start it and try again.
    exit /b 1
)

echo [1/3] Preparing local secrets...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-local-secrets.ps1"
if errorlevel 1 goto :failed

echo [2/3] Building and starting Reactive Resume...
docker compose up -d --build
if errorlevel 1 goto :failed

echo [3/3] Waiting for the web application...
set /a attempts=0
:wait_for_health
set /a attempts+=1
for /f "usebackq delims=" %%H in (`docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" reactive-resume-reactive-resume-1 2^>nul`) do set "health=%%H"
if /i "%health%"=="healthy" goto :ready
if %attempts% GEQ 30 goto :timeout
timeout /t 2 /nobreak >nul
goto :wait_for_health

:ready
echo.
echo Reactive Resume is ready: http://localhost:3000
start "" "http://localhost:3000"
exit /b 0

:timeout
echo WARNING: The containers started, but the application did not become healthy within 60 seconds.
echo Run: docker compose logs --tail 100 reactive-resume
exit /b 1

:failed
echo.
echo ERROR: Reactive Resume could not be started.
exit /b 1
