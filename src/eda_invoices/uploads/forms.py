from django import forms

from eda_invoices.uploads.models import UserUpload


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


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = UserUpload
        fields = ("email",)
