\copy (
  update offer
  set "jsonData" = product."jsonData"
  from product
  where
    offer."productId" = product.id
    and offer."lastProviderId" is not null
    and offer."dateCreated" > '2023-07-25T06:00:00'
    and offer.id > 95020000
    and offer."jsonData"->>'ean' = '9782348036200'
    and product.id between :PRODUCT_ID_MIN and (:PRODUCT_ID_MIN + :BATCH_SIZE)
  returning offer.id
) to '/tmp/fixed_offer_ids_:PRODUCT_ID_MIN.csv'
