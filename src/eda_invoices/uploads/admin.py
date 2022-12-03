from django.contrib import admin

from .models import UserUpload


@admin.register(UserUpload)
class UserUploadAdmin(admin.ModelAdmin):
    search_fields = ("short_uuid", "uuid", "email", "data_file")
    list_display = ("shortened_short_uuid", "data_file", "created", "updated")
    readonly_fields = ("short_uuid", "created", "updated")
