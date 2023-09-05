\copy (
    UPDATE product
    SET "jsonData" = jsonb_set(
        product."jsonData",
        '{gtl_id}',
        to_jsonb(lpad(product."jsonData"->>'gtl_id', 8, '0')),
        true
    ) WHERE product.id between :PRODUCT_ID_MIN and (:PRODUCT_ID_MIN + :BATCH_SIZE)
      AND length(product."jsonData"->>'gtl_id') is not null
      AND length(product."jsonData"->>'gtl_id') < 8
  returning product.id
) to 'fixed_gtl_id_of_product_ids_:PRODUCT_ID_MIN.csv'