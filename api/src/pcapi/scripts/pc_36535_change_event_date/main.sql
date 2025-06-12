UPDATE stock
SET
    "beginningDatetime" = (
        SELECT "beginningDatetime"
        FROM stock
        WHERE "offerId" = 320698795
        AND id = 340541263
    ),
    "dateModified" = now()
WHERE "offerId" = 303524865
AND id = 322955264
;
