#!/bin/sh

git diff $(git rev-parse master) --name-only --relative |\
    grep -E '\.(js|jsx|ts|tsx)$' |\
    grep -v '/api/gen/' |\
    xargs yarn prettier --write
