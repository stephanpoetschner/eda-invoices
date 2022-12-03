import dataclasses
import datetime

from django.conf import settings
from django.db import transaction
from django.http import Http404
from django.shortcuts import render

from eda_invoices.calculations import calc
from eda_invoices.calculations.config import reader as config_reader
from eda_invoices.invoices.models import Invoice


def _abs_path(path):
    return settings.BASE_DIR / "../.." / path


def render_invoice_list(request, upload_id):
    from eda_invoices.uploads.models import UserUpload

    try:
        user_upload = UserUpload.objects.get(short_uid=upload_id)
    except UserUpload.DoesNotExist:
        raise Http404() from None

    with transaction.atomic():
        with user_upload.conf_file.open() as conf_file:
            config = config_reader.parse_config(conf_file)
        with user_upload.data_file.open() as eda_export_file:
            data = calc.clean_data(eda_export_file)

        for ctx in calc.prepare_invoices(
            config,
            data,
            invoice_date=datetime.date.today(),
            invoice_number="1234567890123",
        ):
            invoice = Invoice(user_upload=user_upload, data=dataclasses.asdict(ctx))
            invoice.save()

    return render(
        request,
        "invoices/list.html",
        {
            "invoice": invoice,
        },
    )


def render_invoice(request, upload_id, invoice_id):
    try:
        invoice = Invoice.objects.get(
            short_uuid=invoice_id, upload__short_uuid=upload_id
        )
    except Invoice.DoesNotExist:
        raise Http404() from None

    return render(request, "invoices/invoice.html", invoice.data)
