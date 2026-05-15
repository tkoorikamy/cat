@echo off
setlocal
if not exist .venv (
  py -3.11 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python tools\generate_assets.py
python -m PyInstaller --noconfirm --windowed --name CatCompanion --add-data "assets;assets" --icon assets\tray_icon.png main.py

echo Build done. Check dist\CatCompanion\CatCompanion.exe
