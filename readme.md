# Quuppa API Examples

This is a set of examples about the spirit and particulars of the Quuppa Positioning API

```bash
#Setup python virtual environment (highly recommended to leave virtual environment name to venv for gitignore!!!)
python3 -m venv venv

#activate venv
source ./venv/bin/activate

#drop virtual environment
deactivate

#Install pytest and dev requirements (requires python 3)
pip install -r requirements.txt

#run all tests
pytest

```

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
