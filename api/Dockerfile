##################### Local environment layer #####################

FROM python:3.9.7-slim AS api-flask

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/local/bin

RUN apt-get update \
	&& apt-get -y install gcc libpq-dev libffi-dev xmlsec1 libxmlsec1-openssl \
	&& apt-get clean

COPY ./requirements.txt ./

RUN pip install \
	--no-cache-dir \
	--requirement ./requirements.txt

##################### GCP run layer #####################

FROM api-flask

COPY --from=us-docker.pkg.dev/berglas/berglas/berglas:latest /bin/berglas /bin/berglas

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get -y install postgresql-client curl git && \
    apt-get clean

RUN apt update && \
		apt install -y wget gnupg2 && \
		wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
		echo "deb http://apt.postgresql.org/pub/repos/apt/ `. /etc/os-release && echo $VERSION_CODENAME`-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
		apt update && apt -y install postgresql-client-12 && \
		apt clean

COPY . .

RUN pip install \
	--no-cache-dir \
	--editable .

ENTRYPOINT exec /bin/berglas exec -- ./entrypoint.sh
