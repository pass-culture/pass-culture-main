########## BUILDER ##########

FROM python:3.10-slim AS builder

RUN apt-get update \
	&& apt-get -y install \
		gcc \
		libpq-dev  && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists*

RUN useradd -rm -d /home/pcapi -u 1000 pcapi

USER pcapi

ENV PYTHONUNBUFFERED 1

ENV PATH=$PATH:/home/pcapi/.local/bin
ENV PATH=$PATH:/usr
# Configure Poetry
ENV POETRY_VERSION=1.3.2
ENV POETRY_HOME=/home/pcapi/
ENV POETRY_VENV=/home/pcapi/poetry-venv
ENV POETRY_CACHE_DIR=/home/pcapi/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION} psycopg2

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

COPY poetry.lock pyproject.toml ./

# Install dependencies
# FIXME: don't install dev dependencies
RUN python3 -m venv $POETRY_VENV \
    && poetry install

USER pcapi

WORKDIR /usr/src/app

########## SOURCES ##########

FROM python:3.10-slim AS sources

RUN mkdir -p /tmp/src

WORKDIR /tmp/src

COPY . .

RUN rm -rf tests/

######### LIB ##########

FROM python:3.10-slim AS lib

RUN useradd -rm -d /home/pcapi -u 1000 pcapi

ENV PATH=$PATH:/home/pcapi/.local/bin

RUN apt-get update \
	&& apt-get --no-install-recommends -y install \
		libglib2.0-0 \
		libpango-1.0-0 \
		libpangoft2-1.0-0 \
		libpq5 \
		libxmlsec1-openssl \
		xmlsec1 && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists*

COPY --from=builder /home/pcapi/.local /home/pcapi/.local


WORKDIR /usr/src/app

COPY --from=sources /tmp/src .

RUN chown -R pcapi:pcapi .

USER pcapi

######### DEV ##########

FROM lib AS api-flask

USER root

RUN apt-get update && \
    apt-get --no-install-recommends -y install postgresql-client  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

USER pcapi

RUN poetry install

######### PRODUCTION #########

FROM lib AS pcapi

WORKDIR /usr/src/app

COPY --chown=pcapi:pcapi --from=builder /home/pcapi/poetry-venv/ /home/pcapi/poetry-venv/

USER pcapi
RUN . /home/pcapi/poetry-venv/bin/activate && poetry install

ENTRYPOINT exec ./entrypoint.sh

######### CONSOLE #########

FROM pcapi AS pcapi-console

USER root

RUN apt update && \
    apt install --no-install-recommends -y curl less gnupg2 && \
    curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/pgsql.gpg && \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/pgsql.gpg] http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && \
    echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt update && \
    apt --no-install-recommends -y install postgresql-client-12 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

USER pcapi

######### TESTS #########

FROM pcapi-console AS pcapi-tests

USER root

RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

COPY --chown=pcapi:pcapi tests/ tests
COPY --chown=pcapi:pcapi pyproject.toml .

USER pcapi
