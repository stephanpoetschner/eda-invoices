from django.urls import reverse_lazy


class UseruploadUrlMixin:
    def get_absolute_url(self):
        return reverse_lazy(
            "render_invoice_list",
            kwargs={
                "upload_id": self.short_uuid,
            },
        )

    def get_default_tariff_url(self):
        return reverse_lazy(
            "upload_file_default_tariff",
            kwargs={
                "upload_id": self.short_uuid,
            },
        )

    def get_update_customer_url(self, active_customer=None):
        active_customer = active_customer or 0
        return reverse_lazy(
            "upload_file_customer",
            kwargs={
                "upload_id": self.short_uuid,
                "active_customer": active_customer,
            },
        )

    def get_update_sender_url(self):
        return reverse_lazy("upload_file_sender", kwargs={"upload_id": self.short_uuid})

    def get_thanks_url(self):
        return reverse_lazy(
            "upload_file_thanks",
            kwargs={
                "upload_id": self.short_uuid,
            },
        )
