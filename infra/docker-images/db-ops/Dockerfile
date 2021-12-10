ARG  BASE_PCAPI_TAG
FROM europe-west1-docker.pkg.dev/passculture-infra-prod/pass-culture-artifact-registry/pcapi:${BASE_PCAPI_TAG}

RUN apt-get update \
  && apt-get install -y wget \
                        gnupg2 \
                        zip \
                        ca-certificates \
  && apt-get clean

COPY ./requirements.txt /scripts/requirements.txt
WORKDIR /scripts
RUN pip3 install -r requirements.txt

COPY . /scripts

WORKDIR /usr/src/app

ENV PCAPI_ROOT_PATH /usr/src/app
ENV IMPORT_USERS_SCRIPT_PATH /usr/src/app/src/pcapi/scripts/beneficiary/import_users.py

ENV ANONYMIZE_SQL_SCRIPT_PATH /scripts/anonymize.sql
ENV USERS_CSV_PATH /scripts/data_pass-culture-api-staging.csv

ENTRYPOINT []
CMD []
