@echo off
if not exist .venv (
  py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install -r requirements.txt
python tools\generate_assets.py
python main.py
