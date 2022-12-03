from django.db import models
from django.dispatch import receiver

from eda_invoices.web.models import MyBaseModel


class Invoice(MyBaseModel, models.Model):
    user_upload = models.ForeignKey(
        "uploads.UserUpload", on_delete=models.SET_NULL, null=True, blank=True
    )
    data = models.JSONField(default=dict, blank=True)

    def email(self):
        return self.user_upload.email


@receiver(models.signals.pre_save, sender=Invoice, dispatch_uid="update_short_uuid")
def my_callback(instance, **kwargs):
    instance.update_short_uuid()
