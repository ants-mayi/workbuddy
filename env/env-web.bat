@echo off
chcp 65001 >nul
title Local Dev Env - Web Console
cd /d "G:\AI\WorkBuddy\env"
"G:\workIns\conda\envs\pytorch\python.exe" "engine\web.py"
if errorlevel 1 pause
