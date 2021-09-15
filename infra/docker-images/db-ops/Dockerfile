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

ENTRYPOINT /bin/bash
