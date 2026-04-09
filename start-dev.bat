@echo off
setlocal
chcp 65001 >nul
cls

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_HEALTH_URL=http://127.0.0.1:8000/health"
set "FRONTEND_URL=http://127.0.0.1:5173/"

echo =====================================
echo Dashboard dev startup
echo =====================================
echo.
echo This script starts:
echo   - backend on 8000
echo   - Vite dev server on 5173
echo.

call :ensure_backend
if errorlevel 1 goto :end

echo.

call :ensure_frontend
if errorlevel 1 goto :end

echo.
echo =====================================
echo Dev services are ready
echo Frontend: %FRONTEND_URL%
echo Backend : %BACKEND_HEALTH_URL%
echo =====================================
goto :end

:ensure_backend
call :is_backend_healthy
if not errorlevel 1 (
    echo [OK] Backend already running on port 8000.
    exit /b 0
)

call :is_port_listening 8000
if not errorlevel 1 (
    echo [ERROR] Port 8000 is already in use, but it is not this dashboard backend.
    echo Close the conflicting process, then rerun this script.
    exit /b 1
)

echo [1/2] Starting backend on port 8000...
start "Dashboard Backend" cmd /k "cd /d ""%ROOT_DIR%"" && python server.py"
call :wait_for_backend
if errorlevel 1 (
    echo [ERROR] Backend did not become healthy in time.
    echo Check the "Dashboard Backend" window for details.
    exit /b 1
)

echo [OK] Backend is ready.
exit /b 0

:ensure_frontend
call :is_frontend_healthy
if not errorlevel 1 (
    echo [OK] Vite dev server already running on port 5173.
    exit /b 0
)

call :is_port_listening 5173
if not errorlevel 1 (
    echo [ERROR] Port 5173 is already in use, but it is not the Vite dev server for this project.
    echo Close the conflicting process, then rerun this script.
    exit /b 1
)

echo [2/2] Starting Vite dev server on port 5173...
start "Dashboard Frontend Dev" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"
call :wait_for_frontend
if errorlevel 1 (
    echo [ERROR] Frontend did not become healthy in time.
    echo Check the "Dashboard Frontend Dev" window for details.
    exit /b 1
)

echo [OK] Frontend is ready.
exit /b 0

:is_port_listening
netstat -ano | findstr /R /C:":%~1 .*LISTENING" >nul
exit /b %errorlevel%

:is_backend_healthy
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { $response = Invoke-WebRequest -UseBasicParsing -Uri '%BACKEND_HEALTH_URL%' -TimeoutSec 2; $content = $response.Content; if ($response.StatusCode -eq 200 -and $content -match '\"serialPort\"' -and $content -match '\"serialConnected\"') { exit 0 } else { exit 1 } } catch { exit 1 }"
exit /b %errorlevel%

:is_frontend_healthy
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { $response = Invoke-WebRequest -UseBasicParsing -Uri '%FRONTEND_URL%' -TimeoutSec 2; $content = $response.Content; if ($response.StatusCode -eq 200 -and $content -match '/@vite/client') { exit 0 } else { exit 1 } } catch { exit 1 }"
exit /b %errorlevel%

:wait_for_backend
for /L %%i in (1,1,10) do (
    call :is_backend_healthy
    if not errorlevel 1 exit /b 0
    timeout /t 1 >nul
)
exit /b 1

:wait_for_frontend
for /L %%i in (1,1,15) do (
    call :is_frontend_healthy
    if not errorlevel 1 exit /b 0
    timeout /t 1 >nul
)
exit /b 1

:end
echo.
pause
endlocal
