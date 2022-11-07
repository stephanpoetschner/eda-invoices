import datetime
import pathlib

import click
import django
import pandas as pd
from django.template import loader
from django.utils.text import slugify

from eda_invoices.calculations.calc import parse_raw_data
from eda_invoices.calculations.calc import split_by_metering_point
from eda_invoices.costumers.utils import read_config
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

    config = read_config(yaml_conf)
    headers, df = parse_raw_data(eda_export)

    all_metering_data = dict(split_by_metering_point(headers, df))

    starts_at: datetime.date = df.index[0]
    stops_at: datetime.date = df.index[-1]

    for customer in config["customers"]:
        filename = (
            f"{slugify(customer.customer_id)} -"
            f" {starts_at.isoformat()}-{stops_at.isoformat()} .html"
        )
        metering_data = [
            (point, all_metering_data.get(point.point_id, pd.DataFrame()))
            for point in customer.metering_points
        ]
        print(customer)
        print(metering_data)

        with open(dst / filename, "w") as f:
            html_output = loader.render_to_string(
                "home.html",
                {
                    "sender": config["sender"],
                    "customer": customer,
                    "metering_data": metering_data,
                    "starts_at": starts_at,
                    "stops_at": stops_at,
                },
            )
            f.write(html_output)
