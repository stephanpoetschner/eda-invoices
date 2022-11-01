import click
import yaml
from eda_invoices.calculations.calc import parse_data


@click.command()
@click.argument('yaml_conf, file', type=click.Path(exists=True))
@click.argument('eda_export_file', type=click.Path(exists=True))
def cmd(yaml_conf_file, eda_export_file):
    with open(yaml_conf_file) as f:
        configuration = yaml.safe_load(f)
    import ipdb; ipdb.set_trace
    for df in parse_data(eda_export_file):

        print(df)
        import ipdb;ipdb.set_trace()


if __name__ == '__main__':
    cmd()
