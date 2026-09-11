@echo off
setlocal
title Mahrem - Claude Baglantisi
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\connect-claude.ps1"
pause
