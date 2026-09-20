@echo off
title CodeAlpha Task 1 - Book Catalogue Scraper
cd /d "%~dp0"
echo Installing required Python packages...
py -3 -m pip install -r requirements.txt
if errorlevel 1 python -m pip install -r requirements.txt
echo.
echo Scraping the complete 50-page catalogue. This collects 1,000 listings and product details.
py -3 scrape.py --max-pages 50 --workers 12
if errorlevel 1 python scrape.py --max-pages 50 --workers 12
if errorlevel 1 goto :error
py -3 analyze.py 2>nul || python analyze.py
py -3 build_dashboard.py 2>nul || python build_dashboard.py
start "" "%~dp0index.html"
echo.
echo Complete. The refreshed dashboard is opening now.
pause
exit /b 0
:error
echo.
echo The scraper could not finish. Check your internet connection and Python installation.
pause
exit /b 1
