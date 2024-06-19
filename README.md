# ContentBlock
ContentBlock allows you to hide content you don't want to see.
Improve your browsing experience now!

## Installation

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
$ venv\Scripts\pip install -r requirements_dev.txt

# Linux
$ venv/bin/pip install -r "requirements_dev.txt"
````

Enable UTF-8 support:

> The virtual environment needs to be activated first, as explained in [Execution](#execution)

````shell
# Windows
$ set PYTHONUTF8=1

# Linux
$ export PYTHONUTF8=1
````

If the Naive Bayes classifier has not been initialized (its classifier.pickle file is missing),
then execute the following steps:
````shell
venv\Scripts\activate
cd classifiers/naive_bayes
python create_classifier.py
````

## Execution
Activate virtual environment:
````shell
# Windows
$ venv\Scripts\activate

# Linux
$ source venv/bin/activate
````

Start up application:
````shell
# Windows
$ python cblock.py
````

## Supported web pages
The following web pages are currently supported:
* yahoo.com
* news.yahoo.com
* apnews.com
* cnn.com
* nbcnews.com
* msn.com
* eu.usatoday.com