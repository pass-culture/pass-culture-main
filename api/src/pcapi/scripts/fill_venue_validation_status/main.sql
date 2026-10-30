UPDATE venue
SET "validationStatus" = (
    CASE
        WHEN offerer."validationStatus" IN ('NEW', 'PENDING') THEN 'PENDING'
        WHEN offerer."validationStatus" IN ('VALIDATED', 'CLOSED') THEN 'APPROVED'
        WHEN offerer."validationStatus" = 'REJECTED' THEN 'REJECTED'
    END
)
FROM offerer
WHERE offerer.id = venue."managingOffererId"
AND venue."validationStatus" IS NULL;

UPDATE venue
SET state = 'CLOSED'
FROM offerer
WHERE offerer.id = venue."managingOffererId"
AND offerer."validationStatus" = 'CLOSED'
AND venue.state IS NULL;
