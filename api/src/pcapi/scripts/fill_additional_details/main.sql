UPDATE collective_stock
SET
    "servicePrice" = "price";

UPDATE collective_offer
SET
    "additionalDetails" = collective_stock."priceDetail"
FROM
    collective_stock
WHERE
    collective_offer.id = collective_stock."collectiveOfferId";