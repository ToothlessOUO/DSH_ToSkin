@echo off
setlocal
set HERE=%~dp0
set DST=C:\Program Files\ZCode\resources\app.asar
set BAK=%HERE%out\app.asar.zone-bak

if not exist "%BAK%" (
  echo [x] 没有备份 %BAK% 可恢复。
  pause & exit /b 1
)
copy /y "%BAK%" "%DST%" >nul
if errorlevel 1 ( echo [x] 写入失败，请以管理员身份运行 & pause & exit /b 1 )
echo [OK] 已恢复官方原版 UI。请完全退出 ZCode 后重新打开。
pause
