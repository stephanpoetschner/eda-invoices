import datetime
import pathlib

import click
import django
import pandas as pd
from django.template import loader
from django.utils.text import slugify

from eda_invoices.calculations.calc import group_by_month
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
    df = parse_raw_data(eda_export)

    starts_at: datetime.date = (df.index[0]).date()
    stops_at: datetime.date = (df.index[-1]).date()

    # prices_consumption = pd.DataFrame(
    #     {"prices_buying": [0.1, 0.5]},
    #     index=[
    #         pd.Timestamp("01-01-21 13:30:00.023"),
    #         pd.Timestamp("01-01-25 13:30:00.023"),
    #     ],
    # )
    #
    # prices_generation = pd.DataFrame(
    #     {"prices_selling": [0.4]},
    #     index=[
    #         pd.Timestamp("01-01-21 13:30:00.023"),
    #     ],
    # )
    # if energy_direction == "CONSUMPTION":
    #     data = add_prices(data, prices_consumption)
    # elif energy_direction == "GENERATION":
    #     data = add_prices(data, prices_generation)

    df = group_by_month(df)
    all_metering_data = split_by_metering_point(df)
    for customer in config["customers"]:
        filename = (
            f"{slugify(customer.customer_id)} -"
            f" {starts_at.isoformat()}-{stops_at.isoformat()} .html"
        )
        metering_data = []
        for point in customer.metering_points:
            energy_direction, data = all_metering_data.get(
                point.point_id, (None, pd.DataFrame())
            )
            metering_data.append((point, data))

        total_pricing_data = None
        print(customer)
        print(metering_data)

        with open(dst / filename, "w") as f:
            html_output = loader.render_to_string(
                "home.html",
                {
                    "sender": config["sender"],
                    "customer": customer,
                    "starts_at": starts_at,
                    "stops_at": stops_at,
                    "metering_data": metering_data,
                    "total_pricing_data": total_pricing_data,
                    "invoice_number": "1234567890123",
                    "invoice_date": datetime.date.today(),
                },
            )
            f.write(html_output)
