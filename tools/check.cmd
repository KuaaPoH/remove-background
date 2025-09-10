@echo off
setlocal EnableExtensions

REM 0) Kiểm tra Git & repo
git --version >nul 2>&1 || (echo [ERR] Chua cai Git hoac Git khong nam trong PATH. & goto :end)
git rev-parse --is-inside-work-tree >nul 2>&1 || (echo [ERR] Thu muc nay khong phai Git repo. & goto :end)

REM 1) Đang ở nhánh nào?
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"

REM 2) Chỉ kiểm tra nhánh main
if /i not "%BRANCH%"=="main" (
  echo [WARN] Ban dang o nhanh "%BRANCH%".
  echo Chi kiem tra nhanh main. Hay chay:
  echo     git checkout main
  goto :end
)

REM 3) Fetch remote (khong merge)
git fetch origin >nul 2>&1

REM 4) Phai co origin/main
git show-ref --verify --quiet "refs/remotes/origin/main" || (
  echo [ERR] Khong tim thay origin/main. Repo co the dang dung 'master'.
  echo Neu dung master, hay chay:  git checkout master
  goto :end
)

REM 5) So sanh commit HEAD vs origin/main
for /f "delims=" %%a in ('git rev-parse HEAD') do set "LOCAL=%%a"
for /f "delims=" %%a in ('git rev-parse origin/main') do set "REMOTE=%%a"

if "%LOCAL%"=="%REMOTE%" (
  echo [OK] Ban dang o nhanh main va DA cap nhat moi nhat.
) else (
  echo [WARN] Nhanh main dang CU so voi origin/main.
  echo Cap nhat bang:
  echo     git pull --rebase origin main
)

:end
endlocal
