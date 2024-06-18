@echo off
ECHO Welcome to ContentBlock
:: activate Virtual Environment
call .\venv\Scripts\activate.bat
:: enable utf-8 support
set PYTHONUTF8=1
:: launch application
python cblock.py
pause