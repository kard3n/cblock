@echo off
ECHO Installing ContentBlock
ECHO 
ECHO Create Virtual Environment
python -m venv venv
ECHO Cloning mitmproxy
git clone https://github.com/mitmproxy/mitmproxy.git
ECHO Installing dependencies for mitmproxy
venv\Scripts\pip install -e mitmproxy\.[dev]
ECHO Installing dependencies for ContentBlock
venv\Scripts\pip install -r requirements_dev.txt
ECHO Installation finished
pause