import datetime

from django.db import transaction

from eda_invoices.calculations import calc
from eda_invoices.calculations.calc import split_by_metering_point
from eda_invoices.calculations.calc import to_df
from eda_invoices.calculations.config import reader as config_reader
from eda_invoices.invoices.models import Invoice


def read_metering_points(user_upload):
    with user_upload.data_file.open("r") as eda_export_file:
        data = calc.clean_data(eda_export_file, n=100)

    df = to_df(data)
    all_metering_data = split_by_metering_point(df)
    return all_metering_data


def recreate_invoices(user_upload):
    with transaction.atomic():
        configuration = {
            "sender": user_upload.sender,
            "customers": user_upload.customers,
            "tariffs": user_upload.tariffs,
            "bbc": "",
        }
        config = config_reader.parse_config(configuration)
        with user_upload.data_file.open("r") as eda_export_file:
            data = calc.clean_data(eda_export_file)

        user_upload.invoice_set.all().delete()

        for ctx in calc.prepare_invoice_data(
            config,
            data,
            invoice_date=datetime.date.today(),
            invoice_number="1234567890123",
        ):
            invoice = Invoice(user_upload=user_upload, data=ctx)
            invoice.save()
        user_upload.refresh_from_db()
    return user_upload


def find_fields(fields):
    for field_name in fields:
        new_name = field_name
        if not isinstance(field_name, str):
            field_name, new_name = field_name
        yield field_name, new_name


def convert_dict(data, fields):
    new_data = {}
    for field_name, new_name in find_fields(fields):
        new_data[new_name] = data[field_name]
    return new_data
