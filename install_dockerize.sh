#!/bin/bash

export DOCKERIZE_VERSION=${1:-'v0.6.1'}
wget https://github.com/jwilder/dockerize/releases/download/"$DOCKERIZE_VERSION"/dockerize-linux-amd64-"$DOCKERIZE_VERSION".tar.gz
sudo tar -C /usr/local/bin -xzvf dockerize-linux-amd64-"$DOCKERIZE_VERSION".tar.gz
rm dockerize-linux-amd64-"$DOCKERIZE_VERSION".tar.gz
