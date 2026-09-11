@echo off
setlocal
title Mahrem Kurulum
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-windows.ps1"
if errorlevel 1 (
  echo.
  echo Kurulum tamamlanamadi. Yukaridaki mesaji kontrol edin.
  pause
  exit /b 1
)
echo.
echo Kurulum tamamlandi. Acilan baglanti rehberini izleyin.
pause
