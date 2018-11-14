#!/bin/sh

# ------
# Download Fontello CSS/Font Files to public folder
# @see https://github.com/ryantsangai/fontello-cli
#
# yarn fontello => "./scripts/fontello.sh"
#
OUTPUT_BASE_FOLDER=./public/static/fontello
CONFIG_PATH=$OUTPUT_BASE_FOLDER/config.json
SESSION_PATH=$OUTPUT_BASE_FOLDER/.fontello.session

node ./node_modules/.bin/fontello install --config $CONFIG_PATH --session $SESSION_PATH --css $OUTPUT_BASE_FOLDER/css --font $OUTPUT_BASE_FOLDER/font
