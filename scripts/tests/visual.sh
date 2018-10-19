#!/bin/sh

# ------------------------
# Run TestCafe visual comparaison between images
#
# ---
# USAGE:
# `yarn test:visual`
#
# ---
# NOTE:
# l'option `--force` n'est pas passer via le script.sh
# Utiliser directement la ligne de commande testcafe
# `./node_modules/.bin/testcafe [...options] --force`


function executeCommand () {
  BROWSER='chrome:headless'
  OUTPUT_PATH=testcafe/screenshots
  SCRIPT_FILE=scripts/tests/screenshots-compare.js
  ./node_modules/.bin/testcafe $BROWSER $SCRIPT_FILE -s $OUTPUT_PATH $1
}

# while test $# -gt 0; do
case "$1" in
  -f|--force)
    executeCommand --force
    exit 0
    ;;
  *)
    executeCommand
    exit 0
    ;;
esac
# done

exit 0;
