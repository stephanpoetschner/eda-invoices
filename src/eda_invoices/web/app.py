import datetime
import pathlib
import sys

from decouple import config
from django.conf import settings
from django.shortcuts import render
from django.urls import path

BASE_DIR = pathlib.Path(__file__).parent.resolve()


def setup():
    # settings
    settings.configure(
        # SECURITY WARNING: keep the secret key used in production secret!
        SECRET_KEY=config(
            "SECRET_KEY",
            "django-insecure-$$*z)a47oh#tgihk25$ddvxt!jd)am5b3!px3a3)%j*0k$10v8",
        ),
        DEBUG=config("DEBUG", cast=bool, default=True),
        ALLOWED_HOSTS=config("DEBUG", default="*").split(
            ";"
        ),  # e.g. www.example.com;example.com
        ROOT_URLCONF=__name__,
        WSGI_APPLICATION="eda_invoices.web.wsgi.application",
        MIDDLEWARE=[],
        INSTALLED_APPS=[
            "django.contrib.sessions",
            "django.contrib.staticfiles",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [BASE_DIR / "templates"],
                "APP_DIRS": False,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                    ],
                },
            },
        ],
        STATICFILES_STORAGE=config(
            "STATICFILES_STORAGE",
            default="django.contrib.staticfiles.storage.StaticFilesStorage",
        ),
        STATICFILES_DIRS=[
            BASE_DIR / "static",
        ],
        STATIC_ROOT=config("STATIC_ROOT", default=BASE_DIR / "staticfiles"),
        STATIC_URL="/static/",
        LANGUAGE_CODE="de-at",
        TIME_ZONE="UTC",
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
        USE_THOUSAND_SEPARATOR=True,
    )


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# views
def render_invoice(request, metering_point_id):
    from eda_invoices.calculations import calc
    from eda_invoices.calculations.config import reader as config_reader

    yaml_conf = "samples/costumers.yaml"
    eda_export = "samples/musterenergiedatenexcel.xlsx - ConsumptionDataReport.csv"

    with open(yaml_conf) as f:
        config = config_reader.parse_config(f)
    df = calc.parse_raw_data(eda_export)

    for template_path, ctx in calc.prepare_invoices(
        config, df, invoice_date=datetime.date.today(), invoice_number="1234567890123"
    ):
        metering_point_ids = [
            metering_point_id
            for (metering_point_id, energy_direction, data) in ctx["metering_data"]
        ]
        if metering_point_id in metering_point_ids:
            return render(request, template_path, ctx)


# urls
urlpatterns = [
    path("<str:metering_point_id>", render_invoice, name="render_invoice"),
]

# run the app
if __name__ == "__main__":
    setup()
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
