import pandas as pd
from django.conf import settings
from django.shortcuts import render

from eda_invoices.calculations.config import data
from eda_invoices.uploads.decorators import adds_invoice
from eda_invoices.uploads.decorators import adds_user_upload
from eda_invoices.uploads.utils import recreate_invoices


def _abs_path(path):
    return settings.BASE_DIR / "../.." / path


@adds_user_upload
def render_invoice_list(request, user_upload):
    if not user_upload.invoice_set.exists():
        user_upload = recreate_invoices(user_upload)

    return render(
        request,
        "invoices/list.html",
        {
            "user_upload": user_upload,
        },
    )


@adds_invoice
def render_invoice(request, invoice):
    def _convert_metering_data(data):
        for metering_point, energy_direction, df_data in data:
            df = pd.DataFrame(**df_data)
            df.index = pd.to_datetime(df.index)
            yield metering_point, energy_direction, df

    return render(
        request,
        "invoices/invoice.html",
        {
            "starts_at": invoice.starts_at,
            "stops_at": invoice.stops_at,
            "invoice_date": invoice.invoice_date,
            "invoice_number": invoice.invoice_number,
            "customer": data.Customer(**invoice.customer),
            "sender": data.Sender(**invoice.sender),
            "metering_data": list(_convert_metering_data(invoice.metering_data)),
        },
    )
