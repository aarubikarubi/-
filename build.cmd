@echo off
echo Building main application...
pyinstaller --noconfirm --onedir --windowed --icon=assets/icon.ico --name "DailyGameLauncher" main.py

echo Building updater...
pyinstaller --noconfirm --onefile --windowed --icon=NONE --name "updater" updater.py

echo.
echo Build complete. 
echo To create the installer, compile DailyGameLauncher.iss using Inno Setup.
pause
