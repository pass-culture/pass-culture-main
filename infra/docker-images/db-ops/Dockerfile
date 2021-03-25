ARG  BASE_PCAPI_TAG
FROM europe-west1-docker.pkg.dev/passculture-infra-prod/pass-culture-artifact-registry/pcapi:${BASE_PCAPI_TAG}

RUN apt-get update \
  && apt-get install -y wget \
                        gnupg2 \
                        zip \
                        ca-certificates \
  && apt-get clean

### Install gcloud

ARG GCLOUD_VERSION=318.0.0

ENV GCLOUD_BASE_URL=https://dl.google.com/dl/cloudsdk/channels/rapid/downloads
ENV GCLOUD_TAR_FILE=google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz

RUN wget -q -c ${GCLOUD_BASE_URL}/${GCLOUD_TAR_FILE} -O gcp-cli.tar.gz \
  && tar -xzf gcp-cli.tar.gz \
  && mv google-cloud-sdk/ /usr/local/bin \
  && /usr/local/bin/google-cloud-sdk/install.sh  --quiet \
  && rm -rf gcp-cli.tar.gz

ENV PATH="/usr/local/bin/google-cloud-sdk/bin:$PATH"

COPY ./dump_restore.sh /scripts/dump_restore.sh
COPY ./anonymize.sql /scripts/anonymize.sql

RUN chmod 700 /scripts/dump_restore.sh

WORKDIR /usr/src/app

ENTRYPOINT /bin/bash
