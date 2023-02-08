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
    name = forms.CharField(label=_("Customer name"))

    address_line = forms.CharField(label=_("Address line"))
    address_post_code = forms.CharField(label=_("Post code"))
    address_city = forms.CharField(label=_("City"))

    email = forms.EmailField()

    external_customer_id = forms.CharField(label=_("External id"), required=False)

    active_metering_points = forms.MultipleChoiceField(
        label=_("Active metering points"), choices=()
    )

    add_more = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, metering_points, *args, **kwargs):
        super().__init__(*args, **kwargs)
        metering_points = ((x, x) for x in metering_points)
        self.fields["active_metering_points"].choices = metering_points

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
        new_data |= {
            "default_tariff": "default",
        }
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


class DefaultTariffForm(forms.Form):
    unit_price = forms.DecimalField(label=_("Unit price (€/kWh)"))


class UpdateSenderDetailsForm(forms.Form):
    name = forms.CharField(
        label=_("Your organizations name"),
        help_text=_("e.g. Sonnenstrom Beispiel GmbH"),
    )

    address_line = forms.CharField(
        label=_("Address line"), help_text=_("e.g. Sonnenstraße 1")
    )
    address_post_code = forms.CharField(label=_("Post code"))
    address_city = forms.CharField(label=_("City"))

    email = forms.EmailField(
        label=_("Your email address"),
        help_text=_(
            "The email address on your invoices and we will send you an email with a"
            " link to your invoice data."
        ),
    )
    web = forms.URLField(
        required=False,
        label=_("Your website"),
        help_text=_("We will link to your website on the invoice."),
    )
    phone = forms.CharField(
        required=False,
        label=_("Your phone contact details"),
        help_text=_("We will include your phone number on the invoice."),
    )

    vat_id = forms.CharField(
        required=False,
        label=_("Your VAT ID"),
        help_text=_("We will include your VAT ID on the invoice."),
    )

    @staticmethod
    def to_json(data):
        new_data = convert_dict(
            data,
            [
                "email",
                "name",
                "web",
                "phone",
                "vat_id",
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
        new_data |= {
            "default_tariff": "default",
        }
        return new_data

    @staticmethod
    def from_json(data):
        new_data = convert_dict(
            data,
            [
                "email",
                "name",
                "web",
                "phone",
                "vat_id",
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
