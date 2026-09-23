@echo off
setlocal EnableExtensions
cd /d %~dp0

echo ============================================================
echo SLOPESHIELD NER - one-click full-stack startup
echo ============================================================

where node >nul 2>&1
if errorlevel 1 goto :node_missing

where npm >nul 2>&1
if errorlevel 1 goto :npm_missing

where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 goto :python_missing
)

if not exist "node_modules" (
  echo [1/6] Installing frontend dependencies...
  call npm install
  if errorlevel 1 goto :frontend_fail
) else (
  echo [1/6] Frontend dependencies already installed.
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [2/6] Creating Python virtual environment...
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -m venv backend\.venv
  ) else (
    python -m venv backend\.venv
  )
  if errorlevel 1 goto :python_fail
) else (
  echo [2/6] Python virtual environment already exists.
)

call backend\.venv\Scripts\activate.bat
if errorlevel 1 goto :python_fail
python -m pip install --upgrade pip
if errorlevel 1 goto :python_fail
python -m pip install -r backend\requirements.txt
if errorlevel 1 goto :python_fail

if not exist "backend\.env" copy /Y "backend\.env.example" "backend\.env" >nul

where docker >nul 2>&1
if not errorlevel 1 (
  echo [3/6] Docker detected - starting PostGIS...
  docker compose -f backend\docker-compose.yml up -d
  if errorlevel 1 (
    echo Docker could not start PostGIS. Falling back to local SQLite.
    powershell -NoProfile -Command "(Get-Content 'backend\.env') -replace '^DATABASE_URL=.*','DATABASE_URL=sqlite:///./SLOPESHIELD.db' | Set-Content 'backend\.env'"
  ) else (
    powershell -NoProfile -Command "(Get-Content 'backend\.env') -replace '^DATABASE_URL=.*','DATABASE_URL=postgresql+psycopg://SLOPESHIELD:SLOPESHIELD@localhost:5432/SLOPESHIELD' | Set-Content 'backend\.env'"
  )
) else (
  echo [3/6] Docker not found - using local SQLite fallback.
  powershell -NoProfile -Command "(Get-Content 'backend\.env') -replace '^DATABASE_URL=.*','DATABASE_URL=sqlite:///./SLOPESHIELD.db' | Set-Content 'backend\.env'"
)

echo [4/6] Starting SLOPESHIELD API first...
start "SLOPESHIELD API" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000"

set API_READY=0
for /l %%N in (1,1,30) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health -TimeoutSec 1; if($r.StatusCode -eq 200){exit 0}else{exit 1} } catch { exit 1 }"
  if not errorlevel 1 (
    set API_READY=1
    goto :api_ready
  )
  timeout /t 1 /nobreak >nul
)

:api_ready
if "%API_READY%"=="1" (
  echo [5/6] API is ready on http://127.0.0.1:8000
) else (
  echo [5/6] API did not become ready. The API window is open for the exact error.
  echo The frontend will still be started.
)

if not exist "backend\data\processed\location_features.csv" (
  echo [6/6] Starting real-data bootstrap in a separate window...
  start "SLOPESHIELD DATA PIPELINE" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && call scripts\run_real_pipeline.bat"
) else (
  echo [6/6] Existing processed data found - skipping bootstrap.
)

start "SLOPESHIELD FRONTEND" cmd /k "cd /d %~dp0 && npm run dev -- --host 127.0.0.1"
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:5173
exit /b 0

:frontend_fail
echo Frontend dependency installation failed. Check your internet connection.
pause
exit /b 1

:python_fail
echo Python setup failed. Install Python 3.11+ and run this file again.
pause
exit /b 1

:node_missing
echo Node.js is required. Install Node.js 20 LTS or newer from https://nodejs.org/ and run this file again.
pause
exit /b 1

:npm_missing
echo npm is required. Reinstall Node.js 20 LTS or newer from https://nodejs.org/ and run this file again.
pause
exit /b 1

:python_missing
echo Python 3.11 or newer is required. Install it from https://www.python.org/downloads/ and run this file again.
pause
exit /b 1
