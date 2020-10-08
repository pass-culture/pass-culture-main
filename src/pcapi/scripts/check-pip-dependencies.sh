#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

pip list --outdated > dependencies-outdated.txt

if [[ -s dependencies-outdated.txt ]]; then
    cat dependencies-outdated.txt
    exit 1
else
    echo "Everything is up-to-date !"
fi