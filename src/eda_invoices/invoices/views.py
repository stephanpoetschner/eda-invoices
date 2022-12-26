import datetime

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django.shortcuts import render

from eda_invoices.calculations import calc
from eda_invoices.calculations.config import reader as config_reader
from eda_invoices.invoices.models import Invoice
from eda_invoices.uploads.models import UserUpload


def _abs_path(path):
    return settings.BASE_DIR / "../.." / path


def render_invoice_list(request, upload_id):
    try:
        user_upload = UserUpload.objects.get(short_uuid=upload_id)
    except UserUpload.DoesNotExist:
        raise Http404() from None

    if not user_upload.invoice_set.exists():
        with transaction.atomic():
            with user_upload.conf_file.open("r") as conf_file:
                config = config_reader.parse_config(conf_file)
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

    return render(
        request,
        "invoices/list.html",
        {
            "user_upload": user_upload,
        },
    )


def render_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(short_uuid=invoice_id)
    except Invoice.DoesNotExist:
        raise Http404() from None

    def _convert_metering_data(data):
        for metering_point, energy_direction, df_data in data:
            df = pd.DataFrame(**df_data)
            df.index = pd.to_datetime(df.index)
            yield metering_point, energy_direction, df

    invoice.data["metering_data"] = list(
        _convert_metering_data(invoice.data["metering_data"])
    )

    return render(request, "invoices/invoice.html", invoice.data)
