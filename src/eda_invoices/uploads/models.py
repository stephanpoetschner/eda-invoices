from django.db import models
from django.dispatch import receiver

from eda_invoices.web.models import MyBaseModel


class UserUpload(MyBaseModel, models.Model):
    data_file = models.FileField()
    conf_file = models.FileField()

    def __str__(self):
        return self.shortened_short_uuid()


@receiver(models.signals.pre_save, sender=UserUpload, dispatch_uid="update_short_uuid")
def my_callback(instance, **kwargs):
    instance.update_short_uuid()
