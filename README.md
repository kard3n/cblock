# ContentBlock
ContentBlock allows you to hide content you don't want to see.
Improve your browsing experience now!

## Development

### Installation
Prerequisites: Python 3.12.x, PDM

#### Using PDM
Run `pdm install` from a terminal to create a new virtual environment and install all the necessary dependencies.

#### Manual
```shell
python -m venv .venv
.venv\Scripts\pip install -e ../cblock
```

#### Training the classifiers
If the classifiers have not been trained, you must do so before attempting to start the application.
For the default classifiers, you can use the following commands:
````shell
.venv\Scripts\activate
python classifiers\naive_bayes\create_classifier.py
python classifiers\nb_multilang\train_classifiers.py
````


### Running
#### Using PDM
ContentBlock can be started by executing `pdm run run`.

#### Manual
Alternatively, you can manually activate the virtual environment and then run cblock_main.py
````shell
.venv\Scripts\activate
set PYTHONUTF8=1
python cblock_main.py
````


### Packaging/Installer creation
> For this, you need to have InnoSetup installed.

Run `npm run build`. The executable can then be found in the _Output_ folder.

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