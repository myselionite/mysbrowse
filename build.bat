@echo off
REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    pip install pyinstaller
)

REM Install dependencies from requirements.txt
echo Installing dependencies...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    exit /b 1
)

REM Create the executable
echo Building the executable...
pyinstaller --onefile --noconsole mysbrowse.py

IF %ERRORLEVEL% EQU 0 (
    echo Build successful! Check the "dist" folder for the executable.
) ELSE (
    echo Build failed.
)

pause
