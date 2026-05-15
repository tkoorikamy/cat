@echo off
if not exist .venv (
  py -3.11 -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
python tools\generate_assets.py
python main.py
