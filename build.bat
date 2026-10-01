@echo off
setlocal

python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name WinClean run_gui.py

echo.
echo Build complete.
echo EXE: dist\WinClean.exe
pause
