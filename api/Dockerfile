ARG network_mode=default
########## BUILDER ##########

FROM python:3.11-slim AS builder

RUN apt-get update \
    && apt-get -y install \
    gcc \
    g++ \
    libgdal-dev \
    libpq-dev  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

RUN useradd -rm -d /home/pcapi -u 1000 pcapi

USER pcapi

ENV PYTHONUNBUFFERED 1

COPY ./pyproject.toml ./poetry.lock ./

ENV PATH=$PATH:/home/pcapi/.local/bin

FROM builder AS builder-proxy

COPY /cacert.pem /cacert.pem

RUN REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem pip install poetry

WORKDIR /home/pcapi

RUN poetry check --lock

ENV VIRTUAL_ENV=/home/pcapi/.local

RUN python -m venv $VIRTUAL_ENV

RUN REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem poetry install --without dev --no-root

FROM builder AS builder-default

RUN pip install poetry

WORKDIR /home/pcapi

RUN poetry check --lock

ENV VIRTUAL_ENV=/home/pcapi/.local

RUN python -m venv $VIRTUAL_ENV

RUN poetry install --without dev --no-root

########## DEV BUILDER ##########

FROM builder-${network_mode} AS builder-dev-proxy

RUN poetry check --lock

RUN REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem poetry install --only dev

FROM builder-${network_mode} AS builder-dev-default

RUN poetry check --lock

RUN poetry install --only dev

########## SOURCES ##########

FROM python:3.11-slim AS sources

RUN mkdir -p /tmp/src

WORKDIR /tmp/src

COPY . .

RUN rm -rf tests/ pyproject.toml

######### LIB ##########

FROM python:3.11-slim AS lib

RUN useradd -rm -d /home/pcapi -u 1000 pcapi

ENV PATH=$PATH:/home/pcapi/.local/bin
ENV PROMETHEUS_MULTIPROC_DIR /tmp
ENV FLASK_PROMETHEUS_EXPORTER_PORT 5002

RUN apt-get update \
    && apt-get --no-install-recommends -y install \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpq5 \
    libxmlsec1-openssl \
    xmlsec1

WORKDIR /usr/src/app

COPY --from=sources --chown=pcapi:pcapi /tmp/src .

RUN chown pcapi:pcapi /usr/src/app

USER pcapi

########## LIB PROD ##########

FROM builder-${network_mode} AS builder-prod

FROM lib AS lib-prod

COPY --from=builder-prod /home/pcapi/.local /home/pcapi/.local

########## LIB DEV ##########

FROM builder-dev-${network_mode} AS builder-dev

FROM lib AS lib-dev

COPY --from=builder-dev /home/pcapi/.local /home/pcapi/.local

######### DEV ##########

FROM lib-dev AS api-flask

USER root

RUN apt-get --no-install-recommends -y install curl postgresql-client libgdal-dev

USER pcapi

RUN pip install --no-cache-dir --user -e .

######### PRODUCTION #########

FROM lib-prod AS pcapi

WORKDIR /usr/src/app

RUN pip install \
    --no-cache-dir \
    --editable .

ENTRYPOINT exec ./entrypoint.sh

######### CONSOLE #########

FROM pcapi AS pcapi-console

USER root

RUN apt-get install --no-install-recommends -y curl less gnupg2 && \
    curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/pgsql.gpg && \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/pgsql.gpg] http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && \
    echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && \
    apt-get --no-install-recommends -y install postgresql-client-15 google-cloud-sdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

USER pcapi

######### TESTS #########

FROM api-flask AS pcapi-tests

USER root

RUN apt-get install -y git npm --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

COPY --chown=pcapi:pcapi tests/ tests
COPY --chown=pcapi:pcapi pyproject.toml .

USER pcapi

RUN npm config set prefix "$HOME/.local/"
RUN npm install --global squawk-cli
