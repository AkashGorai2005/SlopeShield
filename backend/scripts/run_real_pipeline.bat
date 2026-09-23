@echo off
cd /d %~dp0..\
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 echo Run this from the project startup script or create backend\.venv first.
python scripts\bootstrap_real_data.py
if errorlevel 1 exit /b 1
python ml\train.py
if errorlevel 1 exit /b 1
exit /b 0
