ARG network_mode=default

########## SOURCES FILES ##########

FROM python:3.11-slim AS source-files

RUN mkdir -p /tmp/src

WORKDIR /tmp/src

COPY . .

RUN rm -rf tests/

########## BUILDERS #########

# Use a dedicated dependency stage to optimize layer caching
FROM python:3.11-slim AS builder-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.7.4 /uv /uvx /bin/

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
    gcc \
    g++ \
    libgdal-dev \
    libpq-dev && \
    apt clean && rm -rf /var/lib/apt/lists*  # reduce image size

########## DEFAULT NETWORK BUILDER #########

FROM builder-dependencies AS builder-default

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter across both images
ENV UV_PYTHON_DOWNLOADS=0

# Display python outputs in real time, without a buffer
ENV PYTHONUNBUFFERED=1

# Install as user instead of root
RUN useradd -rm -d /home/pcapi -u 1000 pcapi
USER pcapi

WORKDIR /usr/src/app

########## PROXY NETWORK BUILDER ##########

FROM builder-default AS builder-proxy

# Set up the proxy network
COPY /cacert.pem /cacert.pem
ENV REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem SSL_CERT_FILE=/cacert.pem

########## PRODUCTION APP BUILDER ##########

FROM builder-${network_mode} AS builder

# Install the project's dependencies
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY --from=source-files --chown=pcapi:pcapi /tmp/src /usr/src/app
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=1000,gid=1000 \
    uv sync --locked --no-dev

########## DEV APP BUILDER ##########

FROM builder AS builder-dev

# Install the project's dev dependencies
RUN --mount=type=cache,target=/home/pcapi/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --only-dev


######### IMAGES ##########

FROM python:3.11-slim AS image-dependencies

RUN useradd -rm -d /home/pcapi -u 1000 pcapi

ENV PATH="/usr/src/app/.venv/bin:/$PATH"
ENV PROMETHEUS_MULTIPROC_DIR=/tmp
ENV FLASK_PROMETHEUS_EXPORTER_PORT=5002

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
    curl \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpq5 \
    libxmlsec1-openssl \
    xmlsec1 && \
    apt-get clean && rm -rf /var/lib/apt/lists*  # reduce image size

WORKDIR /usr/src/app

RUN chown pcapi:pcapi /usr/src/app

COPY --from=builder --chown=pcapi:pcapi /usr/src/app /usr/src/app

######### PRODUCTION IMAGE #########

FROM image-dependencies AS pcapi

COPY --from=builder --chown=pcapi:pcapi /usr/src/app /usr/src/app

USER root

RUN curl -o /usr/local/share/ca-certificates/DigiCertGlobalRootG2.crt.pem https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem && \
    update-ca-certificates

USER pcapi

ENTRYPOINT exec ./entrypoint.sh

######### DEV IMAGE ##########

FROM image-dependencies AS api-flask

RUN apt-get update && apt-get --no-install-recommends -y install postgresql-client libgdal-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists*  # reduce image size

COPY --from=builder-dev --chown=pcapi:pcapi /usr/src/app /usr/src/app

USER pcapi

######### CONSOLE IMAGE #########

FROM api-flask AS pcapi-console-proxy

# Setup the proxy network
COPY /cacert.pem /usr/local/share/ca-certificates/cacert.pem
ENV REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem

FROM api-flask AS pcapi-console-default

FROM pcapi-console-${network_mode} AS pcapi-console

USER root

RUN apt-get update && apt install --no-install-recommends -y curl less gnupg2 && \
    curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/pgsql.gpg && \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/pgsql.gpg] http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && \
    echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && \
    apt-get --no-install-recommends -y install postgresql-client-15 google-cloud-sdk && \
    apt-get clean && rm -rf /var/lib/apt/lists*

USER pcapi

######### TESTS IMAGE #########

FROM api-flask AS pcapi-tests-default

USER root

RUN apt-get update && apt-get install -y git npm --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists*

COPY --chown=pcapi:pcapi tests/ tests

USER pcapi

ENV PATH="/home/pcapi/.local/bin:$PATH"
RUN npm config set prefix "/home/pcapi/.local/"


FROM pcapi-tests-default AS pcapi-tests-proxy

COPY /cacert.pem /cacert.pem
ENV NODE_EXTRA_CA_CERTS=/cacert.pem


FROM pcapi-tests-${network_mode} AS pcapi-tests

RUN npm install --global squawk-cli@1.4.0
