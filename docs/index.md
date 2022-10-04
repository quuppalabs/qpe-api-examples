# Welcome to Quuppa API Examples 1.0.0v

For fast usage instructions, in most scripts, after setup:
`python3.10 script.py --help`

## Project Setup on Linux

```python

#setup a virtual environment and activate it

#cd to project root, e.g. ../src

python3.10 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

```

## Commands

```python
# basic usage
python src/replace_me

```

## Tests

The testing frame work in use is pytest

```python

# test invocation
pytest

# suggested invocation
# This will create a coverage estimate in htmlcov directory and a html test status report with a bit more verbosity
pytest -vv --cov=src --cov-report html --html=test_run_report.html --self-contained-html --showlocals
```

Using suggested invocation above, the test run results will be added to test_run_report.html, as well as be printed to the CL.
Additionally htmlcov/index.html can be viewed in a web browser for detailed coverage information.

## Project layout

mkdocs.yml # The configuration file for mkdocs.
pytest.ini # The configuration file for pytest.
requirments.txt # python package requirements
.gitlab-ci.yml # git lab ci pipe line configuration

```python
docs/
    index.md  # the documentation homepage.

src/# source files for the examples
    helpers/ # project specific utilities
    sensortags/ # everything to do with gateway/sensor tags
    standalone_scripts/ # scripts that can be used without any other files

test/ # all the tests for the project

```

## Influx DB

Some examples make use of a "keys.json" file. An example of this can be found in "keys/keys_template.json". If credentials are needed, make a copy of this and name the copy "keys.json" and populate it as described in the examples documentation/comments. Typical usage will load the file and use an entry similar to:

```json
{
    "influx_db_system_monitor": {
        "token": "<your influx token>",
        "org": "<your influx org>",
        "url": "<your url e.g. https://eu-central-1-1.aws.cloud2.influxdata.com>",
        "bucket": "SystemMonitor"
    }
}

```

## Linting - Pylint

Pylint is a free tool that can be installed with:

```console
pip install pylint
```

Pylint is to be used with Google's configuration file:

https://google.github.io/styleguide/pyguide.html - section 2.1

## Code formatter - Black

Black is a free tool that can be installed with:

```console
pip install black
```

Black follows PEP8, but line length can be modified via command line argument:

black --line-length 120 \<file>

## Sensor Tag Tokenizer Requirements

Every Tokenizer module must implement:

- a tags list for manual assignment of tag IDs
- tokens_reg_ex for tokenizing advertising data into regex groups
- process_adv_data function for establishing types ata minimum and any additional required post processing or interpretation
- id_regular_expression for identifying IDs assigned by the manufacturer 

## Documentation

This project uses mkdocs

```bash

#build documentation
$mkdocs build

#serve docs on http://127.0.0.1:8000/
$mkdocs serve

$mkdocs gh-deploy

```

## Formatting

Formatting is enforced via black and documentation generally follows [Google's Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## VSCode Debug Config

```json
"configurations": [
        {
            "name": "Python: with Args",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": [
                
            ]
        }
    ]
```

## Reference



