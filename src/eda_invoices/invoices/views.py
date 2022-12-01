import datetime

from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from eda_invoices.calculations import calc
from eda_invoices.calculations.config import reader as config_reader


def _abs_path(path):
    return settings.BASE_DIR / "../.." / path


# views
def render_invoice(request, customer_id="12345678"):
    yaml_conf = _abs_path("samples/costumers.yaml")
    eda_export = _abs_path(
        "samples/musterenergiedatenexcel.xlsx - ConsumptionDataReport.csv"
    )

    with open(yaml_conf) as f:
        config = config_reader.parse_config(f)
    data = calc.clean_data(eda_export)

    for template_path, ctx in calc.prepare_invoices(
        config, data, invoice_date=datetime.date.today(), invoice_number="1234567890123"
    ):
        if customer_id == ctx["customer"].customer_id:
            return render(request, template_path, ctx)
    raise Http404()
