SELECT *
FROM offer
    JOIN stock ON offer.id = stock."offerId"
    JOIN venue ON venue.id = offer."venueId"
    JOIN offerer ON offerer.id = venue."managingOffererId"
WHERE offer."isActive"
    AND offer.validation = %(validation_1) s
    AND NOT (
        stock."beginningDatetime" IS NOT NULL
        AND stock."beginningDatetime" <= now()
        OR stock."bookingLimitDatetime" IS NOT NULL
        AND stock."bookingLimitDatetime" <= now()
    )
    AND NOT (
        stock."isSoftDeleted"
        OR stock."beginningDatetime" IS NOT NULL
        AND stock."beginningDatetime" <= now()
        OR CASE
            WHEN (stock.quantity IS NULL) THEN NULL
            ELSE stock.quantity - stock."dnBookedQuantity"
        END IS NOT NULL
        AND CASE
            WHEN (stock.quantity IS NULL) THEN NULL
            ELSE stock.quantity - stock."dnBookedQuantity"
        END <= %(param_1) s
    )
    AND offer."subcategoryId" = %(subcategoryId_1) s
LIMIT %(param_2) s