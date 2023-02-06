import pandas as pd
from django.conf import settings
from django.shortcuts import render

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

    invoice.data["metering_data"] = list(
        _convert_metering_data(invoice.data["metering_data"])
    )

    return render(request, "invoices/invoice.html", invoice.data)
