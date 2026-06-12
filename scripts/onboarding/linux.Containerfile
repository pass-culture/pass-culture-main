FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y
# Basic dependencies:
# - git
# mise:
# - extrepo
# Podman-in-Podman (~= DiD) for in-container containers:
# - fuse-overlayfs
# - podman
# - podman-compose
# Linux-specific dependencies for psycopg2:
# - build-essential
# - libpq-dev
# - python3-dev
#
# Others deps are a simple copy-paste from the Backend Dockerfile (for pango, psycopg2, etc).
RUN apt install --no-install-recommends -y \
  build-essential \
  curl \
  extrepo \
  fuse-overlayfs \
  git \
  libglib2.0-0 \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  libpq-dev \
  libpq5 \
  libxmlsec1-openssl \
  podman \
  podman-compose \
  python3-dev \
  xmlsec1
RUN extrepo enable mise
RUN apt update
RUN apt install -y mise

RUN useradd --create-home --shell /bin/bash bobdupass
USER bobdupass

# Add mise shims to PATH
ENV PATH="/home/bobdupass/.local/share/mise/shims:$PATH"

WORKDIR /home/bobdupass
RUN git clone https://github.com/pass-culture/pass-culture-main

WORKDIR /home/bobdupass/pass-culture-main
COPY --chown=bobdupass:bobdupass ./mise.toml ./mise.toml
RUN mise trust -y && mise install

# Backend
WORKDIR /home/bobdupass/pass-culture-main/api
RUN uv venv --python 3.13 --seed
RUN uv sync

# Frontend
WORKDIR /home/bobdupass/pass-culture-main/pro
RUN pnpm install
