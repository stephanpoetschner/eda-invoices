import yaml

from eda_invoices.costumers import data


def read_config(filename):
    with open(filename) as f:
        configuration = yaml.safe_load(f)

    return {
        'bcc': configuration.get('bcc', None),
        'sender': data.Sender(**configuration.get('sender', {})),
        'customers': [data.Customer(**c) for c in configuration.get('customers', [])],
    }

