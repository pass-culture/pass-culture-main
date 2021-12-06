#!/bin/bash

if [[ "$1" == "production" ]]; then
	echo "passculture.pro"
elif [[ "$1" == "master" ]]; then
	echo "pro.testing.passculture.team"
elif [[  "$1" == "staging" ]]; then
	echo "pro.staging.passculture.team"
elif [[  "$1" == "integration" ]]; then
	echo "integration.passculture.pro"
fi
