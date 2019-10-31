#!/bin/bash

if [[ "$1" == "PC-2478-migration-envs-vers-outscale" ]]; then
	echo "staging"
elif [[ "$1" == "production" ]]; then
	echo "pass-culture-api"
elif [[ "$1" == "master" ]]; then
	echo "pass-culture-api-dev"
elif [[ "$1" == "datalake" ]]; then
	echo "pass-culture-datalake"
elif [[  ! -z "$1" ]]; then
	echo "pass-culture-api-$1"
fi