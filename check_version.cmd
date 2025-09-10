@echo off
setlocal EnableExtensions
chcp 65001 >nul
py -3 "%~dp0banner.py" || python "%~dp0banner.py"
echo.
echo ===============================
echo   KIEM TRA PHIEN BAN DU AN
echo ===============================
echo.

REM ---- Kiểm tra Git có cài chưa
git --version >nul 2>&1 || (
  echo ❌ Chua cai Git. Vui long cai Git tai: https://git-scm.com/downloads
  goto :END
)

REM ---- Kiểm tra có phải repo Git không
git rev-parse --is-inside-work-tree >nul 2>&1 || (
  echo ❌ Day khong phai thu muc Git repo.
  goto :END
)

REM ---- Về nhánh main nếu có
git show-ref --verify --quiet refs/heads/main && git checkout main >nul 2>&1

REM ---- Lấy thông tin mới nhất từ GitHub
echo 🔄 Dang kiem tra cap nhat tu GitHub...
git fetch origin >nul 2>&1

REM ---- So sánh HEAD local với remote
for /f %%i in ('git rev-parse HEAD') do set LOCAL=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE=%%i

if "%LOCAL%"=="%REMOTE%" (
  echo ✅ Ban dang dung phien ban moi nhat.
) else (
  echo ⚠️ Ban dang dung phien ban cu.
  echo 👉 De cap nhat: chay lenh "git pull"
)

:END
echo.
pause
