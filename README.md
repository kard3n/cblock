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

## Packaging/Installer creation
> For this, you need to have both InnoSetup and pyinstaller installed.

First, create the executable file using pyinstaller: `pyinstaller --noconfirm cblock.spec`.

Then, use InnoSetup to load 'inno_Setup.iss' and generate the installer. The executable can then be found in the _Output_ folder.

## Adding schema source repositories
> Currently, only GitHub repositories are supported.
> Schema sources are updated automatically when ContentBlock starts

New schema sources can be added by adding an entry to the _schema_sources.json_ file in the _schemas_ directory.
Entries have the following format: `"{OWNER}/{REPO_NAME}:"{RELEASE_VERSION}"`, where _OWNER_ is the name of the repository owner and _REPO\_NAME_ the name of the repository.
When _RELEASE_VERSION_ is left empty, ContentBlock will automatically get the current version and set the value.

As an example, the entry for the default repository at [github.com/kard3n/cblock_schema](https://github.com/kard3n/cblock_schema), would look like this `"kard3n/cblock_schemas": ""`.

## Supported web pages
The following web pages are currently supported:
* yahoo.com
* news.yahoo.com
* apnews.com
* cnn.com
* nbcnews.com
* msn.com
* eu.usatoday.com