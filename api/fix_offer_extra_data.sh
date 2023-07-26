#!/bin/bash

BATCH_SIZE=500000
PRODUCT_ID_MAX=5000000  # actually: 4998016
product_id_min=0  # actuall: 10048


while [[ $product_id_min < $PRODUCT_ID_MAX ]]
do
    echo "Processing batch starting from $product_id_min"
    # 1. Replace `:PRODUCT_ID_MIN` and `:BATCH_SIZE`.
    # 2. Remove comments (otherwise, when the next step is applied,
    #     the first comment will comment out the rest of the whole
    #     (single) line.
    # 3. Replace "\n" chars by spaces because "\copy" commands must
    #    appear on a single line (and our template uses multiple lines
    #    for clarity)
    cat offer_extra_data_fixer_template.sql | sed -E "s#:BATCH_SIZE#${BATCH_SIZE}#" | sed -E "s#:PRODUCT_ID_MIN#${product_id_min}#g" | sed -E "s#--.*##" | tr "\n" " " | psql ${DATABASE_URL}
    product_id_min=$((product_id_min+BATCH_SIZE))
done
