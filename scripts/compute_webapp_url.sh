#!/bin/bash

if [[ "$1" == "production" ]]; then
	echo "web.passculture.app"
elif [[ "$1" == "master" ]]; then
	echo "web.testing.passculture.team"
elif [[ "$1" == "staging" ]]; then
	echo "web.staging.passculture.team"
elif [[ "$1" == "integration" ]]; then
	echo "web.integration.passculture.app"
fi
