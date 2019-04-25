#!/bin/bash

if [[ "$1" == "production" ]]; then
	echo "passculture.beta.gouv.fr"
elif [[ "$1" == "master" ]]; then
	echo "passculture-testing.beta.gouv.fr"
elif [[  ! -z "$1" ]]; then
	echo "passculture-$1.beta.gouv.fr"
fi