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

REM --- Install required packages for microphone support ---
echo.
echo Installing/Updating required packages...
python -m pip install --upgrade sounddevice numpy SpeechRecognition customtkinter arabic-reshaper python-bidi pyperclip pynput

REM --- Clean old builds ---
echo.
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
echo.
echo Building T-Arabic.exe...
python -m PyInstaller --onefile --noconsole --noconfirm --clean ^
--name=T-Arabic ^
--icon=reverse_melon.ico ^
--version-file=t_arabic_version.txt ^
--hidden-import=arabic_reshaper ^
--hidden-import=bidi.algorithm ^
--hidden-import=pyperclip ^
--hidden-import=customtkinter ^
--hidden-import=speech_recognition ^
--hidden-import=sounddevice ^
--hidden-import=numpy ^
--hidden-import=numpy.core ^
--hidden-import=numpy.core._multiarray_umath ^
--hidden-import=pynput ^
--hidden-import=pynput.keyboard ^
--hidden-import=pynput.keyboard._win32 ^
--hidden-import=_cffi_backend ^
--hidden-import=queue ^
--collect-all=sounddevice ^
reverse_text_app.py

echo.
if exist dist\T-Arabic.exe (
    echo ===============================
    echo     ✅ EXE Build Complete!
    echo     Output: dist\T-Arabic.exe
    echo ===============================
    echo.
    echo IMPORTANT NOTES:
    echo - Microphone support fixed using sounddevice
    echo - Friends need VC++ Redistributable if not installed
    echo - Test microphone with F9 key
    echo ===============================
) else (
    echo ===============================
    echo     ❌ Build Failed!
    echo     Check errors above
    echo ===============================
)

pause