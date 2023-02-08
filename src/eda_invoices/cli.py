import datetime
import pathlib

import click
import django
import yaml
from django.template import loader
from django.utils.text import slugify

from eda_invoices.calculations import calc
from eda_invoices.calculations.config import reader as config_reader
from eda_invoices.web import app


@click.group()
@click.version_option()
def cli():
    """
    Command line tool to analyze CSV data from https://www.eda.at/anwenderportal
    """


@cli.command(name="calc")
@click.argument("yaml_conf", type=click.Path(exists=True))
@click.argument("dst", type=click.Path(exists=True, file_okay=False))
@click.argument("eda_export", type=click.Path(exists=True))
def calc_metering_data(yaml_conf, dst, eda_export):
    app.setup()
    django.setup()

    dst = pathlib.Path(dst)
    with open(yaml_conf) as f:
        config = config_reader.parse_config(yaml.safe_load(f))
    data = calc.clean_data(eda_export)

    template_path = "invoices/invoice.html"

    for ctx in calc.prepare_invoice_data(
        config, data, invoice_date=datetime.date.today(), invoice_number="1234567890123"
    ):
        filename = (
            f"{slugify(ctx['customer'].customer_id)} -"
            f" {ctx['starts_at'].isoformat()}-{ctx['stops_at'].isoformat()} .html"
        )

        with open(dst / filename, "w") as f:
            html_output = loader.render_to_string(template_path, ctx)
            f.write(html_output)
