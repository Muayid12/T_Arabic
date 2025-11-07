@echo off
title Building T-Arabic.exe
echo.
echo ===============================
echo   Building T-Arabic.exe
echo ===============================
echo.

REM --- Check if Python is installed ---
python --version >nul 2>nul
IF ERRORLEVEL 1 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b
)

REM --- Check if PyInstaller is installed ---
where pyinstaller >nul 2>nul || (
    echo PyInstaller not found. Installing...
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
)

REM --- Clean old builds ---
echo Cleaning old builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q T-Arabic.spec 2>nul

REM --- Ensure old exe is deleted ---
if exist dist\T-Arabic.exe (
    echo Deleting old EXE...
    del /f /q dist\T-Arabic.exe
)

REM --- Build the exe ---
echo Building T-Arabic.exe...
python -m PyInstaller --onefile --noconsole --noconfirm --clean ^
--name=T-Arabic ^
--icon=reverse_melon.ico ^
--version-file=t_arabic_version.txt ^
--hidden-import=arabic_reshaper ^
--hidden-import=bidi.algorithm ^
--hidden-import=keyboard ^
--hidden-import=pyperclip ^
--hidden-import=customtkinter ^
reverse_text_app.py

echo.
echo ===============================
echo     ✅ EXE Build Complete!
echo     Output: dist\T-Arabic.exe
echo ===============================
pause
