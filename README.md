# WEB APP

## FOR DEVELOPERS: GETTING STARTED

    $ docker compose run --service-ports django /bin/bash
    $ python ./eda_invoices/manage.py migrate
    $ python ./eda_invoices/manage.py loaddata ../initial_data/auth.yaml
    $ python ./eda_invoices/manage.py runserver 0:8000


# CLI

## RUNNING THE TOOL

    $ pip install -e .
    $ eda_invoices_cli calc samples/costumers.yaml ./output/ samples/musterenergiedatenexcel.xlsx\ -\ ConsumptionDataReport.csv


## FOR DEVELOPERS: GETTING STARTED

    # Create a new virtual env in ./venv
    $ python -m venv ./venv

    # activate newly created virtual env
    $ source venv/bin/activate

    # update pip to latest version and install poetry
    $ pip install --upgrade pip poetry

    # install project dependencies
    $ poetry install

    # install current project
    $ pip install -e .

    # install pre-commit hooks
    $ pre-commit install

    # run tests
    $ poetry run pytest

    $ eda_invoices_cli calc samples/costumers.yaml ./output/ samples/musterenergiedatenexcel.xlsx\ -\ ConsumptionDataReport.csv


### BUILDING WHEELS AND PACKAGES

You may want to build packages for production use. Just run:

    poetry build

And see `dist`-folder.
