@echo off
chcp 65001 >nul
cd /d "G:\AI\WorkBuddy\env"
"G:\workIns\conda\envs\pytorch\python.exe" "engine\cli.py" %*
if errorlevel 1 pause
