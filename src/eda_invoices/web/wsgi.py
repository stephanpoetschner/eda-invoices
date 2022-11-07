"""
WSGI config for eda_invoices project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from eda_invoices.web import app

app.setup()

application = get_wsgi_application()
