UPDATE collective_offer
SET "locationType" = NULL, "offererAddressId" = NULL, "locationComment" = NULL
WHERE True;

UPDATE collective_offer_template
SET "locationType" = NULL, "offererAddressId" = NULL, "locationComment" = NULL
WHERE True;
