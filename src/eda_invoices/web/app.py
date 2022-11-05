import os
import pathlib
import sys

from decouple import config
from django.urls import path
from django.conf import settings
from django.shortcuts import render

BASE_DIR = pathlib.Path(__file__).parent.resolve()


# views
def home(request):
    return render(request, 'home.html')


# urls
urlpatterns = [
    path('', home, name='home'),
]

# settings
settings.configure(
    SECRET_KEY=config('SECRET_KEY', "some-random-key"),
    DEBUG=config('DEBUG', cast=bool, default=True),
    ALLOWED_HOSTS=config('DEBUG', default="").split(";"),  # e.g. www.example.com;example.com
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': False,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                ],
            },
        },
    ],
)

# run the app
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eda_invoices.web.app')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)