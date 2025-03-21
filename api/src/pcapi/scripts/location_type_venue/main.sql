UPDATE collective_offer
SET "locationType" = 'ADDRESS'
WHERE "locationType" = 'VENUE';

UPDATE collective_offer_template
SET "locationType" = 'ADDRESS'
WHERE "locationType" = 'VENUE';
