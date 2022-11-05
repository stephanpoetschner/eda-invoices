import click
import pandas as pd
from eda_invoices.calculations.calc import parse_data
from eda_invoices.costumers.utils import read_config


@click.group()
@click.version_option()
def cli():
    "Command line tool to analyze CSV data from https://www.eda.at/anwenderportal"


@cli.command(name="calc")
@click.argument('yaml_conf', type=click.Path(exists=True))
@click.argument('eda_export', type=click.Path(exists=True))
def calc_metering_data(yaml_conf, eda_export):
    config = read_config(yaml_conf)

    all_metering_data = dict(parse_data(eda_export))

    for customer in config['customers']:
        metering_data = {
            point: all_metering_data.get(point, pd.DataFrame())
            for point in customer.metering_points
        }
        print(customer)
        print(metering_data)

