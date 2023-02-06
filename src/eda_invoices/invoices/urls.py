from django.urls import path

from eda_invoices.invoices.views import render_invoice
from eda_invoices.invoices.views import render_invoice_list

urlpatterns = [
    path(
        "u/<str:upload_id>/",
        render_invoice_list,
        name="render_invoice_list",
    ),
    path("i/<str:invoice_id>/", render_invoice, name="render_invoice"),
]
