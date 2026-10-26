@echo off
setlocal
set HERE=%~dp0
set SRC=%HERE%out\app.asar.zone
set DST=C:\Program Files\ZCode\resources\app.asar
set BAK=%HERE%out\app.asar.zone-bak

if not exist "%SRC%" (
  echo [x] 未找到 %SRC%，请先运行: node build.js
  pause & exit /b 1
)
:: 首次应用时备份当前官方原包（只备份一次）。
:: 注意：若当前已安装的是别的自定义包（如旧版毛玻璃皮肤），此备份捕获的
:: 就是那个包 —— 先用对应 restore 恢复官方版再应用本皮肤。
if not exist "%BAK%" (
  echo 备份当前 app.asar -^> app.asar.zone-bak ...
  copy "%DST%" "%BAK%" >nul
)
copy /y "%SRC%" "%DST%" >nul
if errorlevel 1 ( echo [x] 写入失败，请以管理员身份运行 & pause & exit /b 1 )
echo [OK] ZONE 皮肤已应用。请完全退出 ZCode（托盘图标右键退出）后重新打开。
pause
