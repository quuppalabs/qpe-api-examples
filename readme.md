# Quuppa API Examples

This is a set of examples about the spirit and particulars of the Quuppa Positioning API

```bash
#Setup python virtual environment (highly recommended to leave virtual environment name to venv for gitignore!!!)
python3 -m venv venv

#activate venv (linux)
source ./venv/bin/activate

#activate venv (windows)
cd venv\\Scripts
activate

#drop virtual environment
deactivate

#Install pytest and dev requirements (requires python 3)
pip install -r requirements.txt

#run all tests
pytest

```

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

=======
## Current style related decisions - PEP8

PEP8, except with max line length 120

Black seems to use 88 by default, so this may change even in the near future:
https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html

### Linting - Pylint

Pylint is a free tool that can be installed with:

```console
pip install pylint
```

Pylint is to be used with Google's configuration file:

https://google.github.io/styleguide/pyguide.html - section 2.1

### Code formatter - Black

Black is a free tool that can be installed with:

```console
pip install black
```

Black follows PEP8, but line length can be modified via command line argument:

black --line-length 120 \<file>
>>>>>>> readme.md

## Sensor Tag Tokenizer Requirements

Every Tokenizer module must implement:

- a tags list for manual assignment of tag IDs
- tokens_reg_ex for tokenizing advertising data into regex groups
- process_adv_data function for establishing types ata minimum and any additional required post processing or interpretation
- id_regular_expression for identifying IDs assigned by the manufacturer 
