@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
py -3 -m venv .venv
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install "Pillow==12.3.0"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import tkinter; import PIL"
if errorlevel 1 goto failed
echo Niny is ready. Double-click Launch Niny.vbs to meet her.
if /i "%~1"=="--auto" exit /b 0
pause
exit /b 0
:failed
echo Setup failed. Check the error above. Python 3 with tkinter is required.
pause
exit /b 1
