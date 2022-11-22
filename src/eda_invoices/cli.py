import datetime
import pathlib

import click
import django
import pandas as pd
from django.template import loader
from django.utils.text import slugify

from eda_invoices.calculations import calc
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

    with open(yaml_conf) as f:
        config = read_config(f)
    df = calc.parse_raw_data(eda_export)

    starts_at: datetime.date = (df.index[0]).date()
    stops_at: datetime.date = (df.index[-1]).date()

    prices_consumption = pd.DataFrame(
        {("", "CONSUMPTION", "prices"): [10, 50]},
        index=[
            pd.Timestamp("2021-01-01 00:00:00"),
            pd.Timestamp("2021-03-01 00:00:00"),
        ],
    )

    prices_generation = pd.DataFrame(
        {("", "GENERATION", "prices"): [40]},
        index=[
            pd.Timestamp("2020-01-01 13:30:00"),
        ],
    )
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # df = df["2021-03-01":"2021-03-31"]

    df = calc.add_prices(df, prices_consumption)
    df = calc.add_prices(df, prices_generation)

    for (metering_point_id, energy_direction, type_label), _data in df.items():
        if energy_direction == "CONSUMPTION" and type_label == "local_consumption":
            df[metering_point_id, energy_direction, "local_costs"] = (
                df[metering_point_id, energy_direction, "local_consumption"]
                * df["", energy_direction, "prices"]
            )
        elif energy_direction == "GENERATION" and type_label == "local_generation":
            df[metering_point_id, energy_direction, "local_income"] = (
                df[metering_point_id, energy_direction, "local_generation"]
                * df["", energy_direction, "prices"]
            )

    # df = df.drop(("", "CONSUMPTION", "prices"), axis=1)
    # df = df.drop(("", "GENERATION", "prices"), axis=1)

    all_metering_data = calc.split_by_metering_point(df)
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
            # data = calc.group_by_month(data)
            # data = calc.group_by_day(data)
            # import ipdb; ipdb.set_trace()
            data["local_prices"] = (
                data["local_consumption"] / data["local_costs"]
            ).fillna(0)
            # data = data["2021-03-01":"2021-03-31"]

            metering_data.append((point, energy_direction, data))

        total_pricing_data = None  # TODO: calculate total pricing data
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
