@echo off
setlocal EnableExtensions
chcp 65001 >nul
py -3 "%~dp0banner.py" 2>nul || python "%~dp0banner.py" 2>nul
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
for /f %%i in ('git rev-parse HEAD') do set "LOCAL=%%i"
for /f %%i in ('git rev-parse origin/main') do set "REMOTE=%%i"

if "%LOCAL%"=="%REMOTE%" (
  echo ✅ Ban dang dung phien ban moi nhat.
) else (
  echo ⚠️ Ban dang dung phien ban cu.
  echo 👉 De cap nhat: ghi "git pull" roi Enter
  echo.
  set /p USER_CMD=➡️  Nhap lenh: 

  if /I "%USER_CMD%"=="git pull" (
    echo ⬇️  Dang chay: git pull
    git pull
    if errorlevel 1 (
      echo ❌ Cap nhat that bai.
      echo 💡 Thu meo: neu co thay doi chua commit, thu "git stash" roi chay lai; neu conflict thi giai quyet conflict roi pull lai.
    ) else (
      echo ✅ Cap nhat thanh cong!
    )
  ) else (
    echo ⏭  Khong chay cap nhat vi ban khong nhap "git pull".
  )
)

:END
echo.
pause
