@echo off
setlocal

if not exist .venv (
  py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python tools\generate_assets.py
python tools\generate_assets.py --ico

python -m PyInstaller --noconfirm --windowed --name CatCompanion --add-data "assets;assets" --icon assets\tray_icon.ico main.py

if exist dist\CatCompanion\CatCompanion.exe (
  echo Build done. Check dist\CatCompanion\CatCompanion.exe
) else if exist dist\CatCompanion.exe (
  echo Build done. Check dist\CatCompanion.exe
) else (
  echo Build failed: exe not found in dist
  exit /b 1
)
