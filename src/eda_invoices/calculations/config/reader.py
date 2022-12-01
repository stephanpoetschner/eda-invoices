import yaml

from eda_invoices.calculations.config import data


def parse_config(f):
    configuration = yaml.safe_load(f)
    config = {
        "bcc": configuration.get("bcc", None),
        "sender": data.Sender(**configuration.get("sender", {})),
        "customers": [data.Customer(**c) for c in configuration.get("customers", [])],
        "tariffs": [data.Tariff(**t) for t in configuration.get("tariffs", [])],
    }
    tariff_names = {t.name for t in config["tariffs"]}
    for customer in config["customers"]:
        for mp in customer.metering_points:
            if mp.active_tariff is not None and mp.active_tariff not in tariff_names:
                raise ValueError(
                    f"Customer {customer.name} has unknown tariff {mp.active_tariff}"
                )
    return config
