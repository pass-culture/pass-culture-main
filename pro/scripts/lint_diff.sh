#!/bin/sh

git diff $(git rev-parse master) --name-only --relative |\
    grep -E '\.(js|jsx|ts|tsx)$' |\
    grep -v '/api/v1/gen/' |\
    grep -v '/api/v2/gen/' |\
    xargs yarn prettier --write
