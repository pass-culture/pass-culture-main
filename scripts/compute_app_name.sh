#!/bin/bash

if [[ "$1" == "production" ]]; then
	echo "pass-culture-api"
elif [[ "$1" == "master" ]]; then
	echo "pass-culture-api-dev"
elif [[  ! -z "$1" ]]; then
	echo "pass-culture-api-$1"
fi
