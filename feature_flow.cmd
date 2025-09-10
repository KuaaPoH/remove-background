@echo off
setlocal EnableExtensions
chcp 65001 >nul
py -3 "%~dp0banner.py" || python "%~dp0banner.py"
echo.
echo ===========================================
echo   		PUSH CODE GITHUB
echo ===========================================
echo.

REM --- 1) Kiểm tra git và repo ---
git --version >nul 2>&1 || (echo ❌ Chua cai Git. && goto :END)
git rev-parse --is-inside-work-tree >nul 2>&1 || (echo ❌ Khong phai thu muc Git repo. && goto :END)

REM --- 2) Lấy nhánh hiện tại ---
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURBR=%%i

REM --- 3) Nếu đang ở main/master thì bắt buộc tạo/đổi sang feature ---
if /I "%CURBR%"=="main"  goto :NEED_FEATURE
if /I "%CURBR%"=="master" goto :NEED_FEATURE
goto :HAVE_FEATURE

:NEED_FEATURE
echo ⚠️  Dang o nhanh "%CURBR%". Khong duoc push truc tiep vao main/master.
set /p NEWBR=👉 Nhap ten nhanh tinh nang (vi du: feature-login): 
if "%NEWBR%"=="" (echo ❌ Chua nhap ten nhanh. & goto :END)

REM neu nhanh da ton tai => checkout, khong thi tao moi
git show-ref --verify --quiet refs/heads/%NEWBR%
if %ERRORLEVEL%==0 (
  echo 🔀 Chuyen sang nhanh da co: %NEWBR%
  git checkout %NEWBR%
) else (
  echo 🌱 Tao nhanh moi: %NEWBR%
  git checkout -b %NEWBR%
)
set CURBR=%NEWBR%

:HAVE_FEATURE
echo.
echo ✅ Dang lam viec tren nhanh: %CURBR%
echo.

REM --- 4) Nhap message commit ---
set /p MSG=📝 Nhap noi dung commit: 
if "%MSG%"=="" set MSG=update

REM --- 5) Add + Commit (bo qua commit neu khong co thay doi) ---
echo 🔄 git add .
git add .

echo 🧷 git commit -m "%MSG%"
git commit -m "%MSG%"
if %ERRORLEVEL% NEQ 0 (
  echo (Thong bao tren co the chi ra la khong co gi de commit. Tiep tuc push upstream neu can.)
)

REM --- 6) Push len origin, tu dong -u neu lan dau ---
echo 📤 Dang push len origin/%CURBR% ...
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if %ERRORLEVEL%==0 (
  git push
) else (
  git push -u origin %CURBR%
)

if %ERRORLEVEL% NEQ 0 (
  echo ❌ Push that bai. Kiem tra mang/quyen truy cap.
  goto :END
)

echo ✅ Push thanh cong len origin/%CURBR%.
echo.

REM --- 7) Goi link tao Pull Request tren GitHub (neu xac dinh duoc URL) ---
for /f "tokens=*" %%i in ('git remote get-url origin') do set GITURL=%%i

REM Chuyen SSH -> HTTPS; cat .git; tao URL compare
set REPOURL=%GITURL%
REM truong hop ssh: git@github.com:user/repo.git
echo %REPOURL% | find "git@github.com:" >nul
if %ERRORLEVEL%==0 (
  set REPOURL=https://github.com/%REPOURL:git@github.com:=%
)

REM bo duoi .git neu co
if /I "%REPOURL:~-4%"==".git" set REPOURL=%REPOURL:~0,-4%

REM Xac dinh nhanh chinh (main/master) tu remote
set BASE=main
git ls-remote --heads origin main >nul 2>&1 || set BASE=master

set PRURL=%REPOURL%/compare/%BASE%...%CURBR%?expand=1

echo 🔗 Mo trang tao Pull Request:
echo %PRURL%
start "" "%PRURL%"

:END
echo.
pause
