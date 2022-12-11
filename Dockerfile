# syntax = docker/dockerfile:1.2
ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION} AS python_base


ARG BUILD_ENVIRONMENT \
  # Needed for fixing permissions of files created by Docker:
  UID=1000 \
  GID=1000

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  # pip:
  # PIP_NO_CACHE_DIR=off \
  PIP_CACHE_DIR='/var/cache/buildkit/pip' \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.3.0 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/buildkit/pypoetry' \
  POETRY_HOME='/usr/local'

# https://vsupalov.com/buildkit-cache-mount-dockerfile/
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN mkdir -p $PIP_CACHE_DIR \
    && mkdir -p $POETRY_CACHE_DIR

# System deps:
# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -ex && \
    apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    # psycopg2 dependencies
    libpq-dev \
    # translations
    gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/var/cache/buildkit/ \
    set -ex && \
    pip install --upgrade pip "poetry==$POETRY_VERSION"

WORKDIR /code


FROM python_base as development_build

RUN groupadd -g "${GID}" -r web \
  && useradd -d '/code' -g web -l -r -u "${UID}" web \
  && chown web:web -R '/code' \
  # Static and media files:
  && mkdir -p '/var/www/django/static' '/var/www/django/media' \
  && chown web:web '/var/www/django/static' '/var/www/django/media'

# Copy only requirements, to cache them in docker layer
COPY --chown=web:web ./poetry.lock ./pyproject.toml /code/

FROM development_build as dev_app

RUN --mount=type=cache,target=/var/cache/buildkit/ \
    set -ex && \
    echo "BUILD_ENVIRONMENT" \
    && poetry version \
    && poetry install --no-root \
      $(if [ "BUILD_ENVIRONMENT" = 'production' ]; then echo '--only main'; fi) \
        --no-interaction --no-ansi

COPY . /code/

RUN --mount=type=cache,target=/var/cache/buildkit/ \
    set -ex && \
    echo "BUILD_ENVIRONMENT" \
    && poetry version \
    && poetry install \
      $(if [ "BUILD_ENVIRONMENT" = 'production' ]; then echo '--only main'; fi) \
        --no-interaction --no-ansi

RUN python src/eda_invoices/manage.py collectstatic --noinput

USER web

COPY --chown=web:web . /code

WORKDIR /code/src

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "eda_invoices/web/wsgi.py"]
