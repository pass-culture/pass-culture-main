#!/bin/bash

BATCH_SIZE=500000
PRODUCT_ID_MIN=1  # actuall: 10048
PRODUCT_ID_MAX=5100000  # actually: 5089733

while [[ $PRODUCT_ID_MIN < $PRODUCT_ID_MAX ]]
do
    echo "Processing batch starting from $PRODUCT_ID_MIN"
    # 1. Replace `:PRODUCT_ID_MIN` and `:BATCH_SIZE`.
    # 2. Remove comments (otherwise, when the next step is applied,
    #     the first comment will comment out the rest of the whole
    #     (single) line.
    # 3. Replace "\n" chars by spaces because "\copy" commands must
    #    appear on a single line (and our template uses multiple lines
    #    for clarity)
    cat product_gtl_id_fixer_template.sql | sed -E "s#:BATCH_SIZE#${BATCH_SIZE}#" | sed -E "s#:PRODUCT_ID_MIN#${PRODUCT_ID_MIN}#g" | sed -E "s#--.*##" | tr "\n" " " | psql ${DATABASE_URL}
    PRODUCT_ID_MIN=$((PRODUCT_ID_MIN+BATCH_SIZE))
done