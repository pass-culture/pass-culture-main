FROM python:3.13-slim AS builder
ARG PROXY

COPY ../cacert.pem /cacert.pem

WORKDIR /app

COPY pyproject.toml ./
COPY . .

RUN if [ -z "$PROXY" ]; then \
      pip install .[dev]; \
    else \
      REQUESTS_CA_BUNDLE=/cacert.pem PIP_CERT=/cacert.pem CURL_CA_BUNDLE=/cacert.pem pip install .[dev]; \
    fi

RUN chmod +x entrypoint.sh

ENTRYPOINT ["uvicorn", "src.pcproxy.main:app"]
