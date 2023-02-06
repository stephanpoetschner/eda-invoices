from django import forms
from django.utils.translation import gettext_lazy as _

from eda_invoices.uploads.models import UserUpload
from eda_invoices.uploads.utils import convert_dict


class UserUploadForm(forms.ModelForm):
    class Meta:
        model = UserUpload
        fields = ("data_file",)

    def __init__(self, active_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_user = active_user

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.active_user.is_authenticated:
            instance.email = self.active_user.email

        if commit:
            instance.save()

        instance.update_metering_points()
        if commit:
            instance.save()
        return instance


class CustomerForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(label=_("Customer name"))

    address_line = forms.CharField(label=_("Address line"))
    address_post_code = forms.CharField(label=_("Post code"))
    address_city = forms.CharField(label=_("City"))

    external_customer_id = forms.CharField(label=_("External id"), required=False)

    add_more = forms.BooleanField(required=False, widget=forms.HiddenInput)

    @staticmethod
    def to_json(data):
        new_data = convert_dict(
            data,
            [
                "email",
                "name",
                ("external_customer_id", "customer_id"),
            ],
        )
        new_data["address"] = convert_dict(
            data,
            [
                ("address_line", "line"),
                ("address_post_code", "post_code"),
                ("address_city", "city"),
            ],
        )
        return new_data

    @staticmethod
    def from_json(data):
        new_data = convert_dict(
            data,
            [
                "email",
                "name",
                ("customer_id", "external_customer_id"),
            ],
        )
        new_data |= convert_dict(
            data["address"],
            [
                ("line", "address_line"),
                ("post_code", "address_post_code"),
                ("city", "address_city"),
            ],
        )
        return new_data


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = UserUpload
        fields = ("email",)
