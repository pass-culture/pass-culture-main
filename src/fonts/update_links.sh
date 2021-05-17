#!/bin/bash

#
# Generate (or update) links to font files
#


function update_links() {
    package=$1
    filename_prefix=$2

    link_base_dir=../../node_modules/${package}/files

    for filename in $(ls ${filename_prefix}-*)
    do
        ln --force --symbolic ${link_base_dir}/${filename} ${filename}
    done
}

update_links "@fontsource/barlow" "barlow-latin"
