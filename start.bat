@echo off
chcp 65001 >nul
title MathVideo AI - 수학 영상 추천 시스템

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   📐 MathVideo AI - 수학 영상 추천       ║
echo  ║   Starting servers...                    ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    https://www.python.org/downloads/ 에서 설치해주세요.
    pause
    exit /b 1
)

:: Install Python dependencies
echo [1/3] 📦 Python 패키지 설치 중...
cd /d "%~dp0backend"
pip install -r requirements.txt -q

:: Start backend server
echo [2/3] 🚀 백엔드 서버 시작 중 (포트 8000)...
start "MathVideo-Backend" cmd /k "cd /d %~dp0backend && python main.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend (simple HTTP server)
echo [3/3] 🌐 프론트엔드 서버 시작 중 (포트 3000)...
cd /d "%~dp0frontend"
start "MathVideo-Frontend" cmd /k "python -m http.server 3000"

:: Wait and open browser
timeout /t 2 /nobreak >nul
echo.
echo ✅ 서버가 시작되었습니다!
echo    📌 프론트엔드: http://localhost:3000
echo    📌 백엔드 API: http://localhost:8000/docs
echo.
echo 🌐 브라우저를 열고 있습니다...
start http://localhost:3000

echo.
echo 종료하려면 이 창과 서버 창들을 모두 닫아주세요.
pause
