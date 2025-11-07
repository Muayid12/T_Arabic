@echo off
title Building T-Arabic Installer
echo.
echo ===============================
echo   Building T-Arabic Installer
echo ===============================
echo.

rem === Check if EXE exists ===
if not exist "dist\T-Arabic.exe" (
    echo T-Arabic.exe not found. Please run build_exe.bat first.
    pause
    exit /b
)

rem === Try detecting Inno Setup ===
set "ISCC_PATH="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

rem === Check if found ===
if "%ISCC_PATH%"=="" (
    echo Inno Setup Compiler not found.
    echo Please install it from https://jrsoftware.org/isinfo.php
    pause
    exit /b
)

echo Found Inno Setup at:
echo "%ISCC_PATH%"
echo.
echo Building installer...

rem === Run Inno Setup Compiler ===
call "%ISCC_PATH%" "T-Arabic.iss"

echo.
echo ===============================
echo ✅ Installer Build Complete!
echo Output: Installer\T-Arabic-Setup.exe
echo ===============================
pause
