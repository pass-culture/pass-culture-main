# syntax=docker.io/docker/dockerfile:1.7-labs

ARG network_mode=default
ARG uid=1000

#########################
##   PYTHON BUILDERS   ##
#########################

FROM python:3.13-slim  AS builder-default-network

FROM builder-default-network AS builder-proxy-network

# Set up the proxy network
COPY /cacert.pem /cacert.pem

ENV REQUESTS_CA_BUNDLE=/cacert.pem
ENV PIP_CERT=/cacert.pem
ENV CURL_CA_BUNDLE=/cacert.pem
ENV SSL_CERT_FILE=/cacert.pem
ENV GIT_SSL_CAINFO=/cacert.pem

FROM builder-${network_mode}-network AS builder-dependencies

ARG uid

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

RUN apt-get update && \
  apt-get --no-install-recommends -y install \
  gcc \
  g++ \
  git \
  libgdal-dev \
  libpq-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*  # reduce image size

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter across both images
ENV UV_PYTHON_DOWNLOADS=0

# Install as user instead of root
RUN useradd -rm -d /home/pcapi -u ${uid} pcapi
USER pcapi

WORKDIR /usr/src/app

######### PRODUCTION BUILDER #########

FROM builder-dependencies AS builder-prod

# Install the project's dependencies
COPY --chown=pcapi:pcapi pyproject.toml uv.lock /usr/src/app/
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=${uid},gid=${uid} \
  uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY --chown=pcapi:pcapi --exclude=tests/ ./ /usr/src/app/
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=${uid},gid=${uid} \
  uv sync --locked --no-dev


######### DEV BUILDER #########

FROM builder-dependencies AS builder-dev

ARG uid

# Install the project's dependencies
COPY --chown=pcapi:pcapi pyproject.toml uv.lock /usr/src/app/
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=${uid},gid=${uid} \
  uv sync --locked --dev --no-install-project

# Then, add the rest of the project source code and tests, and install it
# Installing separately from its dependencies allows optimal layer caching
COPY --chown=pcapi:pcapi ./ /usr/src/app/
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=${uid},gid=${uid} \
  uv sync --locked --dev


#######################
##   DOCKER IMAGES   ##
#######################

FROM python:3.13-slim AS image-dependencies-default-network

FROM image-dependencies-default-network AS image-dependencies-proxy-network

# Setup the proxy network
COPY /cacert.pem /cacert.pem
ENV REQUESTS_CA_BUNDLE=/cacert.pem
ENV PIP_CERT=/cacert.pem
ENV CURL_CA_BUNDLE=/cacert.pem


FROM image-dependencies-${network_mode}-network AS image-dependencies

ARG uid

RUN useradd -rm -d /home/pcapi -u ${uid} pcapi

ENV PATH="/usr/src/app/.venv/bin:$PATH"
ENV PROMETHEUS_MULTIPROC_DIR=/tmp
ENV FLASK_PROMETHEUS_EXPORTER_PORT=5002

# Display python outputs in real time, without a buffer
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
  apt-get --no-install-recommends -y install \
  curl \
  libglib2.0-0 \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  libpq5 \
  libxmlsec1-openssl \
  xmlsec1 && \
  apt-get clean && rm -rf /var/lib/apt/lists/*  # reduce image size

WORKDIR /usr/src/app

RUN chown pcapi:pcapi /usr/src/app

######### PRODUCTION IMAGE #########

FROM image-dependencies AS pcapi

RUN curl -o /usr/local/share/ca-certificates/DigiCertGlobalRootG2.crt.pem https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem && \
  update-ca-certificates

USER pcapi

COPY --from=builder-prod --chown=pcapi:pcapi /usr/src/app/ /usr/src/app/

ENTRYPOINT exec ./entrypoint.sh

######### DEV & TESTS IMAGES ##########

FROM image-dependencies AS api-flask

RUN apt-get update && \
  apt-get --no-install-recommends -y install postgresql-client libgdal-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*  # reduce image size

USER pcapi

COPY --from=builder-dev --chown=pcapi:pcapi /usr/src/app/ /usr/src/app/

FROM api-flask AS pcapi-tests

######### CONSOLE IMAGE #########

FROM image-dependencies AS pcapi-console

RUN apt-get update && apt-get install --no-install-recommends -y curl less gnupg2 && \
  curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/pgsql.gpg && \
  echo "deb [signed-by=/etc/apt/trusted.gpg.d/pgsql.gpg] http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && \
  echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
  apt-get update && \
  apt-get --no-install-recommends -y install postgresql-client libgdal-dev postgresql-client-15 google-cloud-sdk && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

USER pcapi

COPY --from=builder-dev --chown=pcapi:pcapi /usr/src/app/ /usr/src/app/
