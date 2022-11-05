import os
import pathlib
import sys

from decouple import config
from django.urls import path
from django.conf import settings
from django.shortcuts import render

BASE_DIR = pathlib.Path(__file__).parent.resolve()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# views
def home(request):
    return render(request, 'home.html')


# urls
urlpatterns = [
    path('', home, name='home'),
]

# settings
settings.configure(
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY=config('SECRET_KEY', "django-insecure-$$*z)a47oh#tgihk25$ddvxt!jd)am5b3!px3a3)%j*0k$10v8"),
    DEBUG=config('DEBUG', cast=bool, default=True),
    ALLOWED_HOSTS=config('DEBUG', default="*").split(";"),  # e.g. www.example.com;example.com
    ROOT_URLCONF=__name__,
    WSGI_APPLICATION='eda_invoices.web.wsgi.application',
    MIDDLEWARE=[],
    INSTALLED_APPS=[
        'django.contrib.sessions',
        'django.contrib.staticfiles',
    ],
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
    STATIC_URL='/static/',
    LANGUAGE_CODE='en-us',
    TIME_ZONE='UTC',
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
)

# run the app
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eda_invoices.web.app')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)