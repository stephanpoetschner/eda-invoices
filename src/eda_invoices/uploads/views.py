from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from eda_invoices.uploads.decorators import adds_user_upload
from eda_invoices.uploads.forms import UpdateEmailForm
from eda_invoices.uploads.forms import UserUploadForm


def upload_file(request):
    form = UserUploadForm(request.user, request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(
            reverse("upload_file_email", kwargs={"upload_id": instance.short_uuid})
        )
    return render(
        request,
        "uploads/generic_form.html",
        {
            "form": form,
        },
    )


@adds_user_upload
def update_email(request, user_upload):
    form = UpdateEmailForm(request.POST or None, instance=user_upload)
    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(
            reverse("upload_file_thanks", kwargs={"upload_id": instance.short_uuid})
        )
    return render(
        request,
        "uploads/generic_form.html",
        {
            "form": form,
        },
    )


def thank_you(request, *args, **kargs):
    return render(request, "uploads/thank_you.html")
