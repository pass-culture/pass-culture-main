########## BUILDER ##########

FROM python:3.9.7-slim AS builder

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
	&& apt-get -y install \
		gcc \
		libpq-dev

COPY ./requirements.txt ./

RUN pip install --user \
	--requirement ./requirements.txt

######### DEV ##########

FROM python:3.9.7-slim AS api-flask

ENV PATH=$PATH:/root/.local/bin

RUN apt-get update \
	&& apt-get --no-install-recommends -y install \
		libglib2.0-0 \
		libpango-1.0-0 \
		libpangoft2-1.0-0 \
		libpq5 \
		libxmlsec1-openssl \
		xmlsec1

COPY --from=builder /root/.local /root/.local

######### PRODUCTION #########

FROM api-flask AS pcapi

WORKDIR /usr/src/app

COPY . .

RUN pip install \
		--no-cache-dir \
		--editable .

ENTRYPOINT exec ./entrypoint.sh

######### CONSOLE #########

FROM pcapi AS pcapi-console

RUN apt-get update && \
    apt-get -y install \
		postgresql-client \
		curl \
		git

RUN apt update && \
	apt install -y wget gnupg2 && \
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
	echo "deb http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
	apt update && apt -y install postgresql-client-12
