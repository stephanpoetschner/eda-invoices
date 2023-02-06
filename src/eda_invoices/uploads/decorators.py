from functools import wraps

from django.http import Http404

from eda_invoices.invoices.models import Invoice
from eda_invoices.uploads.models import UserUpload


def adds_user_upload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Do something before
        upload_id = kwargs.pop("upload_id")
        if not upload_id:
            raise Http404("No upload_id provided")
        try:
            user_upload = UserUpload.objects.get(short_uuid=upload_id)
        except UserUpload.DoesNotExist:
            raise Http404() from None

        kwargs["user_upload"] = user_upload

        result = func(*args, **kwargs)  # Call the decorated function
        return result

    return wrapper


def adds_invoice(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Do something before
        invoice_id = kwargs.pop("invoice_id")
        if not invoice_id:
            raise Http404("No invoice_id provided")
        try:
            invoice = Invoice.objects.get(short_uuid=invoice_id)
        except Invoice.DoesNotExist:
            raise Http404() from None
        kwargs["invoice"] = invoice

        result = func(*args, **kwargs)  # Call the decorated function
        return result

    return wrapper
