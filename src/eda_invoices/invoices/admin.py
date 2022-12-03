from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ("short_uuid", "uuid", "user_upload__email")
    list_display = ("shortened_short_uuid", "email", "created", "updated")
    readonly_fields = ("short_uuid", "created", "updated")
