import uuid

from django.db import models

from eda_invoices.web import utils


class MyBaseModel(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    short_uuid = models.CharField(unique=True, max_length=26, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def update_short_uuid(self):
        self.short_uuid = utils.uuid_to_short_uuid(self.uuid)

    def shortened_short_uuid(self):
        return self.short_uuid[:6]

    class Meta:
        abstract = True
