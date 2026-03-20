@echo off
chcp 65001 >nul
cls

echo =====================================
echo 监测系统启动脚本
echo =====================================
echo.

:: 1. 启动后端服务
echo 1. 启动后端服务...
cd /d "d:\vue5\jiance"
start "Backend Service" cmd /k "python server.py"
echo    后端服务启动中，访问地址: http://localhost:8000

:: 等待后端服务初始化
echo    等待后端服务初始化...
timeout /t 3 >nul

echo.

:: 2. 启动前端服务
echo 2. 启动前端服务...
cd /d "d:\vue5\jiance\frontend"
start "Frontend Service" cmd /k "npm run dev"
echo    前端服务启动中，访问地址: http://localhost:5173

echo.

:: 3. 启动监控服务
echo 3. 启动监控服务...
cd /d "d:\vue5\jiance"
start "Monitor Service" cmd /k "python monitor.py"
echo    监控服务已启动

echo.
echo =====================================
echo 系统启动完成！
echo 请检查每个终端窗口的服务状态。
echo =====================================
echo.
echo 按任意键关闭此窗口...
pause >nul