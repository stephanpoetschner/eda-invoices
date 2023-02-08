import collections

from eda_invoices.calculations.config import data
from eda_invoices.calculations.config import exceptions


def parse_config(configuration):
    config = data.Config(**configuration)
    # Sanity checks
    # ensure only known tariffs are assigned
    tariff_names = {t.name for t in config.tariffs}
    for customer in config.customers:
        for mp in customer.metering_points:
            if mp.active_tariff is not None and mp.active_tariff not in tariff_names:
                raise exceptions.ConfigError(
                    f'Dem Kunden "{customer.name}" ist der unbekannte Tarif'
                    f' "{mp.active_tariff}" zugeordnet.'
                )

    # ensure each customer_id is unique
    duplicate_customer_ids = collections.Counter(
        customer.customer_id for customer in config.customers
    )
    duplicate_customer_ids = {
        k: v for k, v in duplicate_customer_ids.most_common() if v > 1
    }
    if duplicate_customer_ids:
        raise exceptions.ConfigError(
            'Es gibt Kunden mit derselben Kundennummer ("customer_id"): '
            f'{ ",".join(duplicate_customer_ids) }'
        )
    return config
