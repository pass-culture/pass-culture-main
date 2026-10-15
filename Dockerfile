# syntax=docker/dockerfile:1

FROM ubuntu:26.04 AS system

ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID

COPY cacerts/nscacert.pem /usr/local/share/ca-certificates/nscacert.crt
RUN <<EOF
  set -ex
  apt-get update
  apt-get install -y --no-install-recommends \
    git \
    apt-transport-https \
    ca-certificates \
    extrepo \
    curl \
    gnupg2
  update-ca-certificates
EOF

ENV MISE_TRUSTED_CONFIG_PATHS="./mise.toml"
ENV MISE_DATA_DIR="/home/$USERNAME/.mise"
ENV MISE_CONFIG_DIR="/home/$USERNAME/.mise"
ENV MISE_CACHE_DIR="/home/$USERNAME/.mise/cache"
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
ENV PATH="/home/$USERNAME/.mise/shims:$PATH"

USER $USERNAME

