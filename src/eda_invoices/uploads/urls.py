from django.urls import include
from django.urls import path

from eda_invoices.uploads.views import set_default_tariff
from eda_invoices.uploads.views import thank_you
from eda_invoices.uploads.views import update_customer
from eda_invoices.uploads.views import update_sender_information
from eda_invoices.uploads.views import upload_file

urlpatterns = [
    path("", upload_file, name="upload_file"),
    path(
        "<str:upload_id>/",
        include(
            [
                path("", update_customer, name="upload_file_customer"),
                path(
                    "<int:active_customer>/",
                    update_customer,
                    name="upload_file_customer",
                ),
                path("tariff/", set_default_tariff, name="upload_file_default_tariff"),
                path(
                    "organization/",
                    update_sender_information,
                    name="upload_file_sender",
                ),
                path("thanks/", thank_you, name="upload_file_thanks"),
            ]
        ),
    ),
]
