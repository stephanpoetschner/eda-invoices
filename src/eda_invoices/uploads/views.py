from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from eda_invoices.uploads.decorators import adds_user_upload
from eda_invoices.uploads.forms import CustomerForm
from eda_invoices.uploads.forms import DefaultTariffForm
from eda_invoices.uploads.forms import UpdateEmailForm
from eda_invoices.uploads.forms import UserUploadForm


def upload_file(request):
    form = UserUploadForm(request.user, request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save()
        url = reverse(
            "upload_file_default_tariff",
            kwargs={
                "upload_id": instance.short_uuid,
            },
        )
        return HttpResponseRedirect(url)
    return render(
        request,
        "uploads/generic_form.html",
        {
            "form": form,
        },
    )


@adds_user_upload
def set_default_tariff(request, user_upload):
    form = DefaultTariffForm(request.POST or None)
    if form.is_valid():
        user_upload.tariffs = [
            {
                "name": "default",
                "prices": [
                    {
                        "price": float(form.cleaned_data["unit_price"]),
                        "date": "1970-01-01",  # TODO:
                    },
                ],
            }
        ]
        user_upload.save()
        return HttpResponseRedirect(
            reverse(
                "upload_file_customer",
                kwargs={"upload_id": user_upload.short_uuid, "active_customer": 0},
            )
        )
    return render(
        request,
        "uploads/generic_form.html",
        {
            "form": form,
        },
    )


@adds_user_upload
def update_customer(request, user_upload, active_customer=None):
    total_existing_customer = len(user_upload.customers)
    initial_data = None

    if not active_customer:
        return HttpResponseRedirect(
            reverse(
                "upload_file_customer",
                kwargs={"upload_id": user_upload.short_uuid, "active_customer": 1},
            )
        )

    if active_customer > total_existing_customer + 1:
        return HttpResponseRedirect(
            reverse(
                "upload_file_customer",
                kwargs={
                    "upload_id": user_upload.short_uuid,
                    "active_customer": total_existing_customer,
                },
            )
        )
    elif active_customer <= total_existing_customer:
        try:
            initial_data = list(user_upload.customers)[active_customer - 1]
            initial_data = CustomerForm.from_json(initial_data)
        except IndexError:
            pass

    form = CustomerForm(
        metering_points=user_upload.metering_points,
        data=request.POST or None,
        initial=initial_data,
    )
    if form.is_valid():
        customer_data = CustomerForm.to_json(form.cleaned_data)

        tariff_data = form.cleaned_data["active_metering_points"]
        customer_data["metering_points"] = [
            {"point_id": point_id} for point_id in tariff_data
        ]

        if active_customer <= total_existing_customer:
            user_upload.customers[active_customer - 1] = customer_data
        else:
            user_upload.customers = (user_upload.customers or []) + [customer_data]

        user_upload.save()

        if form.cleaned_data.get("add_more"):
            return HttpResponseRedirect(
                reverse(
                    "upload_file_customer",
                    kwargs={
                        "upload_id": user_upload.short_uuid,
                        "active_customer": active_customer + 1,
                    },
                )
            )

        return HttpResponseRedirect(
            reverse("upload_file_email", kwargs={"upload_id": user_upload.short_uuid})
        )
    return render(
        request,
        "uploads/personal_data.html",
        {
            "form": form,
            "active_customer": active_customer,
            "total_existing_customer": total_existing_customer,
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
