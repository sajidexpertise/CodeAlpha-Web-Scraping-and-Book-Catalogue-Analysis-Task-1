@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 goto :failed
%PYTHON% scrape.py
if errorlevel 1 goto :failed
start "" "OPEN_DASHBOARD.html"
echo Completed. The dataset, dashboard and report are updated.
pause
exit /b 0
:failed
echo Scraping failed. Read the message above; the starter dataset is kept.
pause
exit /b 1
