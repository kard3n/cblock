# ContentBlock

## Installation
### With conda:
 > Make sure that python is installed before continuing

Create venv:
````shell
$ python -m venv venv
````

Clone mitmproxy:
````shell
$ git clone https://github.com/mitmproxy/mitmproxy.git
````

Install mitmproxy to environment:
````shell
# Windows
$ venv\Scripts\pip install -e mitmproxy\.[dev]

# Linux
$ venv/bin/pip install -e "mitmproxy/.[dev]"
````

Install cblock's dependencies to environment:
````shell
# Windows
$ venv\Scripts\pip install -r cblock/requirements_dev.txt

# Linux
$ venv/bin/pip install -r "cblock/requirements_dev.txt"
````

## Execution
Activate virtual environment:
````shell
# Windows
$ venv\Scripts\activate

# Linux
$ source venv/bin/activate
````