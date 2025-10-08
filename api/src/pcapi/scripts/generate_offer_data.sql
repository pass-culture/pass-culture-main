-- FIRST TEST 
-- One user, one offerer, one venue, one offer, X stocks, lots of bookings

--NOTES
-- If you want integers, that are >= 1 and < 10, then it's simple:
-- select trunc(random() * 9 + 1)

-- missing USER with first name lastname email phonenumber
-- missing OFFERER userofferer 
-- missing BOOKING "priceCategoryLabel" dateused, "cancellationDate", "cancellationLimitDate", "reimbursementDate", isexternal, isconfirmed
-- missing VENUE proper offerer address
-- missing ALL coherent dates

WITH last_offerer_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM offerer
)
INSERT INTO offerer (
    id,
    "dateCreated",
    name,
    "siren",
    "isActive",
    "validationStatus",
    "allowedOnAdage",
    "postalCode",
    "city"
)
SELECT
    last_offerer_id.last_id + gs AS id,
    now() - (random() * interval '730 days') AS "dateCreated",
    ('Offerer ' || gs)::TEXT AS name,
    (trunc(random() * 999999999 + 100000000))::TEXT AS "siren",
    true AS "isActive",
    'VALIDATED' AS "validationStatus",
    true AS "allowedOnAdage",
    '75000' AS "postalCode",
    'Paris' AS "city"
FROM last_offerer_id, generate_series(1, 1) gs;


WITH last_offerer_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM offerer
),
last_venue_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM venue)
INSERT INTO venue (
    id,
    name,
    "dateCreated",
    "managingOffererId",
    "isPermanent",
    "isOpenToPublic",
    "isVirtual",
    "venueTypeCode",
    "timezone",
    "thumbCount",
    "siret",
    "offererAddressId",
    "dmsToken"
)
SELECT
    last_venue_id.last_id + gs AS id,
    'Venue ' || gs AS name,
    now() - (random() * interval '730 days') AS "dateCreated",
    last_offerer_id.last_id AS "managingOffererId",
    true AS "isPermanent",
    true AS "isOpenToPublic",
    false AS "isVirtual",
    'OTHER' AS "venueTypeCode",
    'Europe/Paris' AS "timezone",
    1 AS "thumbCount",
    (trunc(random() * 999999999999 + 10000000000000))::TEXT AS "siret",
    5 AS "offererAddressId",
    substr(md5(random()::text), 1, 6) AS "dmsToken"
FROM last_venue_id, last_offerer_id, generate_series(1, 1) gs;

WITH last_venue_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM venue
), last_offer_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM offer
)
INSERT INTO offer (
    id,
    "dateCreated",
    "venueId",
    "isActive",
    name,
    "isNational",
    "isDuo",
    "fieldsUpdated",
    validation,
    "subcategoryId",
    "ean"
)
SELECT
    last_offer_id.last_id + gs AS id,
    now() - (random() * interval '720 days') AS "dateCreated",
    last_venue_id.last_id::bigint AS "venueId",
    true AS "isActive",
    'Offer ' || (last_offer_id.last_id + gs) AS name,
    (random() > 0.8) AS "isNational",
    false AS "isDuo",
    ARRAY[]::varchar[] AS "fieldsUpdated",
    'APPROVED'::public.validation_status AS validation,
    (100 + floor(random() * 50))::text AS "subcategoryId",
    NULL AS "ean"
FROM last_offer_id, last_venue_id, generate_series(1, 1) gs;

WITH last_stock_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM stock
), last_offer_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM offer
)
INSERT INTO stock (
    id,
    "dateCreated",
    "dateModified",
    "dnBookedQuantity",
    "offerId",
    "price",
    "features",
    "fieldsUpdated"
)
SELECT
    last_stock_id.last_id + gs AS id,
    now() - (random() * interval '710 days') AS "dateCreated",
    now() - (random() * interval '700 days') AS "dateModified",
    0 AS "dnBookedQuantity",
    last_offer_id.last_id AS "offerId",
    (10 + floor(random() * 90))::bigint AS "price",
    '{}'::text[] AS "features",
    '{}'::text[] AS "fieldsUpdated"
FROM last_stock_id, last_offer_id, generate_series(1, 1) gs;

WITH last_stock_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM stock),
last_booking_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM booking
), last_offerer_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM offerer
), last_venue_id AS (
    SELECT COALESCE(MAX(id), 0) AS last_id FROM venue
)

INSERT INTO booking (
    id,
    "dateCreated",
    "dateUsed",
    "stockId",
    "venueId",
    "offererId",
    "quantity",
    token,
    "userId",
    "amount",
    status
)
SELECT
    last_booking_id.last_id + gs AS id,
    now() - (random() * interval '365 days') AS "dateCreated",
    NULL AS "dateUsed",
    last_stock_id.last_id::bigint AS "stockId",
    last_venue_id.last_id::bigint AS "venueId",
    last_offerer_id.last_id::bigint AS "offererId",
    2 AS "quantity",
    substr(md5(random()::text), 1, 6) AS token,
    (1 + floor(random() * 10))::bigint AS "userId",
    0 AS "amount",
    'CONFIRMED' AS status
FROM last_booking_id, last_offerer_id, last_stock_id, last_venue_id, generate_series(1, 100) gs;
