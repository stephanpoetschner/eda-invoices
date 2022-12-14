import hashlib
import os

from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy

from eda_invoices.web.models import MyBaseModel


def _hash_upload(field_name, instance, filename):
    def _md5_file(file):
        hash_md5 = hashlib.md5()
        for chunk in file.chunks():
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    file_field = getattr(instance, field_name)
    file_field.open()  # make sure we're at the beginning of the file
    md5_name = _md5_file(file_field)
    fname, ext = os.path.splitext(filename)
    return f"{md5_name[:3]}/{md5_name[3:]}.{ ext }"


def upload_data_file(instance, filename):
    return _hash_upload("data_file", instance, filename)


def upload_conf_file(instance, filename):
    return _hash_upload("conf_file", instance, filename)


class UserUpload(MyBaseModel, models.Model):
    data_file = models.FileField(upload_to=upload_data_file)
    conf_file = models.FileField(upload_to=upload_conf_file)
    email = models.EmailField()

    def __str__(self):
        return self.shortened_short_uuid()

    def get_absolute_url(self):
        return reverse_lazy(
            "render_invoice_list",
            kwargs={
                "upload_id": self.short_uuid,
            },
        )


@receiver(models.signals.pre_save, sender=UserUpload, dispatch_uid="update_short_uuid")
def my_callback(instance, **kwargs):
    instance.update_short_uuid()
