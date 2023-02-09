from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy

from eda_invoices.invoices import json_encoder
from eda_invoices.web.models import MyBaseModel


class Invoice(MyBaseModel, models.Model):
    user_upload = models.ForeignKey(
        "uploads.UserUpload", on_delete=models.SET_NULL, null=True, blank=True
    )

    invoice_date = models.DateField(null=True, blank=True)
    stops_at = models.DateTimeField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    invoice_number = models.CharField(max_length=255, null=True, blank=True)

    sender = models.JSONField(
        default=dict, null=True, blank=True, encoder=json_encoder.MyJSONEncoder
    )
    customer = models.JSONField(
        default=dict, null=True, blank=True, encoder=json_encoder.MyJSONEncoder
    )
    metering_data = models.JSONField(
        default=dict, null=True, blank=True, encoder=json_encoder.MyJSONEncoder
    )

    def email(self):
        return self.user_upload.email

    def display_name(self):
        return ", ".join(
            filter(
                None,
                [
                    self.customer.get("name", ""),
                    self.customer.get("address", {}).get("line", ""),
                ],
            )
        )

    def get_absolute_url(self):
        return reverse_lazy(
            "render_invoice",
            kwargs={
                "invoice_id": self.short_uuid,
            },
        )


@receiver(models.signals.pre_save, sender=Invoice, dispatch_uid="update_short_uuid")
def my_callback(instance, **kwargs):
    instance.update_short_uuid()
