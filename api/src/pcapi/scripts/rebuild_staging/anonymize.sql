-- Run from /usr/src/app:
-- psql $DATABASE_URL < src/pcapi/scripts/rebuild_staging/anonymize.sql

\i src/pcapi/scripts/rebuild_staging/first_names.sql
\i src/pcapi/scripts/rebuild_staging/last_names.sql

CREATE OR REPLACE FUNCTION pg_temp.generate_booking_token_from_id(id BIGINT)
 RETURNS VARCHAR(6) AS $$
DECLARE
  -- Same alphabet as in `random_token()` in our Python code.
  -- alphabet char[] = '234567ABCDEFGHJKLMNPQRSTUVWXYZ';
  alphabet char[] = ARRAY['2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
  alphabet_length int = 30;
  len int = 6;
  token varchar(6) = '';
  val bigint = id;
BEGIN
  -- val := id;
  token := '';
  IF val < 0 THEN
          val := val * -1;
  END IF;
  WHILE val != 0 LOOP
    token := alphabet[(val % alphabet_length)+1] || token;
    val := val / alphabet_length;
  END LOOP;
  IF char_length(token) < len THEN
    token := lpad(token, len, '2');
  END IF;
  RETURN token;
END; $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION pg_temp.random_text(len INT)
  RETURNS TEXT AS $$
BEGIN
  RETURN substring(gen_random_uuid()::text, 1, len);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_iban_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN 'FR' || lpad(id::text, 25, '0');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_bic_from_id(id BIGINT)
  -- Generate a fake BIC from the given id
  RETURNS TEXT AS $$
BEGIN
  RETURN 'XXXXXX' || 'X' || lpad(upper(to_hex(id)), 4, '0');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_phone_number_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN '+336' || lpad(id::text, 8, '0');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_id_piece_number_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN lpad(id::text, 12, '0');
END; $$
LANGUAGE plpgsql;

BEGIN;
  -- Temporarily disable trigger to speed up updates.
  ALTER TABLE booking DISABLE TRIGGER stock_update_cancellation_date;
  -- Drop and recreate the token colum to temporarily set all tokens to NULL to avoiding triggering
  -- UNIQUEness error on existing (not yet anonymized) tokens on the
  -- second UPDATE.
  ALTER TABLE booking DROP COLUMN token, ADD COLUMN token VARCHAR(6);
  UPDATE booking SET token = pg_temp.generate_booking_token_from_id(id);
  -- Restore constraints and trigger.
  ALTER TABLE booking ALTER COLUMN token SET NOT NULL;
  ALTER TABLE booking ADD CONSTRAINT booking_token_key UNIQUE (token);
  ALTER TABLE booking ENABLE TRIGGER stock_update_cancellation_date;
COMMIT;

-- Set fake IBAN and BIC in `bank_information` and `payment` table.
UPDATE bank_information SET iban = pg_temp.fake_iban_from_id(id) WHERE iban is not null;
UPDATE bank_information SET bic = pg_temp.fake_bic_from_id(id) WHERE bic is not null;
UPDATE payment
SET iban = pg_temp.fake_iban_from_id(id), bic = pg_temp.fake_bic_from_id(id)
WHERE payment.iban IS NOT NULL
;

UPDATE invoice SET token = 'anonymized-' || id::text;

UPDATE activation_code SET code = 'FAKE-' || id::text ;

UPDATE provider
SET "authToken" = 'anonymized, you may have to set it if you want to use this provider'
WHERE "authToken" IS NOT NULL
;

UPDATE provider
SET 
    "bookingExternalUrl" = 'http://mock-api-billeterie.mock-api-billeterie.svc.cluster.local:5003/tickets/create',
    "cancelExternalUrl" = 'http://mock-api-billeterie.mock-api-billeterie.svc.cluster.local:5003/tickets/cancel'
WHERE "bookingExternalUrl" IS NOT NULL and "cancelExternalUrl" IS NOT NULL;

UPDATE provider
SET 
    "notificationExternalUrl" = 'http://mock-api-billeterie.mock-api-billeterie.svc.cluster.local:5003/notify'
WHERE "notificationExternalUrl" IS NOT NULL;

UPDATE provider
SET 
    "hmacKey" = 's3cr3tK3y'
WHERE "hmacKey" IS NOT NULL;

UPDATE boost_cinema_details
SET
  password = '',
  token = NULL,
  "tokenExpirationDate" = NULL
;

UPDATE cgr_cinema_details SET password = '';

UPDATE cds_cinema_details
SET "cinemaApiToken" = 'anonymized, you may have to set it if you want to use this provider'
;

UPDATE external_booking
SET barcode=ROUND(RANDOM() * 9999999999999)::VARCHAR(13)
;

UPDATE api_key SET secret = pg_temp.random_text(32)::bytea;

UPDATE "user"
SET
    "email" = 'user' || "id" || '@anonymized.email',
    "password" = 'fake-hashed-password'::bytea,
    "firstName" = pg_temp.fake_first_name(id),
    "lastName" = pg_temp.fake_last_name(id),
    "dateOfBirth" = '01/01/2001',
    "validatedBirthDate" = case when "validatedBirthDate" is null then null else '2001-01-01'::timestamp end,
    "idPieceNumber" = case when "idPieceNumber" is null then null else pg_temp.fake_id_piece_number_from_id(id) end,
    "phoneNumber" = pg_temp.fake_phone_number_from_id(id)
WHERE email NOT LIKE '%@passculture.app';
;

UPDATE "user"
SET
    "password" = 'fake-hashed-password'::bytea,
    "dateOfBirth" = '01/01/2001',
    "validatedBirthDate" = case when "validatedBirthDate" is null then null else '2001-01-01'::timestamp end,
    "phoneNumber" = pg_temp.fake_phone_number_from_id(id)
WHERE email LIKE '%@passculture.app';
;

UPDATE "user_email_history"
SET
    "oldUserEmail" = 'old_user' || "id",
    "oldDomainEmail" =  'anonymized.email',
    "newUserEmail" = 'user' || "id",
    "newDomainEmail" = 'anonymized.email'
;

-- Keep those which doesn't contain personal data
UPDATE action_history
SET "jsonData" = '{}'
WHERE "ruleId" is null and "financeIncidentId" is null
;

-- FIXME (dbaty, 2023-05-04): we should anonymize `offer.bookingEmail`
-- but that would take a very long time.
--   UPDATE offer
--   SET
--     "bookingEmail" = 'offer-' || id || '-booking-email@anonymized.email'
--   ;

UPDATE collective_offer
SET
  "bookingEmails" = '{}',
  "contactEmail" = 'offer-' || id || '-contact-email@anonymized.email',
  "contactPhone" = pg_temp.fake_phone_number_from_id(id)
;

UPDATE collective_offer_template
SET
  "bookingEmails" = '{}',
  "contactEmail" = 'template-' || id || '-contact-email@anonymized.email',
  "contactPhone" = pg_temp.fake_phone_number_from_id(id)
;

UPDATE venue
SET
  "dmsToken" = 'dms-token-' || id,
  "bookingEmail" = 'venue-' || id || '-booking-email@anonymized.email',
  "collectiveEmail" = 'venue-' || id || '-collective-email@anonymized.email',
  "collectivePhone" = pg_temp.fake_phone_number_from_id(id)
;

UPDATE venue_contact
SET
  "email" = 'venue-' || id || '-contact-email@anonymized.email',
  phone_number = pg_temp.fake_phone_number_from_id(id)
;

UPDATE educational_institution
SET
  email = 'institution-' || id || '@anonymized.email',
  "phoneNumber" = pg_temp.fake_phone_number_from_id(id)
;

UPDATE educational_redactor
SET
  email = 'redactor-' || id || '@anonymized.email',
  "firstName" = pg_temp.fake_first_name(id),
  "lastName" = pg_temp.fake_last_name(id)
;

-- Delete all other beneficiary_fraud_check rows
DELETE from beneficiary_fraud_check
WHERE "type" not in (
    'JOUVE',
    'EDUCONNECT',
    'UBBLE',
    'DMS',
    'INTERNAL_REVIEW',
    'PHONE_VALIDATION',
    'HONOR_STATEMENT',
    'USER_PROFILING'
  )
;

-- Anonymize beneficiary_fraud_check table content
UPDATE beneficiary_fraud_check
SET "resultContent" = CASE
  WHEN "type" = 'JOUVE'
    THEN "resultContent" || (
        '{"email": "user' || "userId" || '@anonymized.email", "address": "42 rue de la ville", "lastName": "' || pg_temp.fake_last_name("userId") || '", "firstName": "' || pg_temp.fake_first_name("userId") || '", "phoneNumber": "' || pg_temp.fake_phone_number_from_id("userId") || '", "bodyPieceNumber": "000000000000"}'
      )::text::jsonb
  WHEN "type" = 'EDUCONNECT'
    THEN "resultContent" || (
        '{"last_name": "' || pg_temp.fake_last_name("userId") || '", "first_name": "' || pg_temp.fake_first_name("userId") || '"}'
      )::text::jsonb
  WHEN "type" = 'DMS'
    THEN "resultContent" || (
        '{"email": "user' || "userId" || '@anonymized.email", "phone": "' || pg_temp.fake_phone_number_from_id("userId") || '", "address": "42 rue de la ville 44000 Nantes", "last_name": "' || pg_temp.fake_last_name("userId") || '", "first_name": "' || pg_temp.fake_first_name("userId") || '", "id_piece_number": "00000000 1 ZZ0"}'
      )::text::jsonb
  WHEN ("type" = 'UBBLE' AND "status" = 'OK')
    THEN "resultContent" || (
        '{"identification_id": "11111111-1111-4111-9111-111111111111"}'
      )::text::jsonb
  WHEN ("type" = 'UBBLE' AND "status" = 'KO')
    THEN "resultContent" || (
        '{"identification_id": "00000000-0000-4000-8000-000000000000"}'
      )::text::jsonb
  WHEN "type" = 'UBBLE'
    THEN "resultContent" || (
      '{"last_name": "' || pg_temp.fake_last_name("userId") || '", "first_name": "' || pg_temp.fake_first_name("userId") || '", "married_name": "marriedName", "id_document_number": null, "identification_id": "22222222-2222-4222-a222-222222222222", "identification_url": null}'
    )::text::jsonb
  WHEN "type" = 'INTERNAL_REVIEW'
    THEN "resultContent" || (
        '{"phone_number": "' || pg_temp.fake_phone_number_from_id("userId") || '"}'
      )::text::jsonb
  WHEN "type" = 'PHONE_VALIDATION'
    THEN "resultContent" || (
        '{"phone_number": "' || pg_temp.fake_phone_number_from_id("userId") || '"}'
      )::text::jsonb
  WHEN "type" = 'USER_PROFILING'
    THEN "resultContent" || (
        '{"account_email": "user' || "userId" || '@anonymized.email"}'
      )::text::jsonb
  ELSE "resultContent"
END
;

UPDATE orphan_dms_application
SET email = "id" || '@anonymized.email'
;

-- Anonymize beneficiary_fraud_review table content
UPDATE beneficiary_fraud_review
SET reason = ''
WHERE reason is not null
;

TRUNCATE TABLE activity;
TRUNCATE TABLE user_session;

-- Avoid synchronization with providers
UPDATE venue_provider SET "isActive" = false;
-- Deactivate the related offers
-- Analysis of the query: https://passculture.atlassian.net/browse/PC-28443
-- TL;DR: It takes about 100 seconds, and uses the indexes. No seq scan of the offer table is happening.
-- This is the best we can do to avoid a full table scan.
UPDATE offer
SET "isActive" = false
FROM venue_provider
JOIN provider ON provider.id = venue_provider."providerId"
WHERE venue_provider."venueId" = offer."venueId"
  AND provider."localClass" = 'CDSStocks'
;
UPDATE offer
SET "isActive" = false
FROM venue_provider
JOIN provider ON provider.id = venue_provider."providerId"
WHERE venue_provider."venueId" = offer."venueId"
  AND provider."localClass" = 'BoostStocks'
;
UPDATE offer
SET "isActive" = false
FROM venue_provider
JOIN provider ON provider.id = venue_provider."providerId"
WHERE venue_provider."venueId" = offer."venueId"
  AND provider."localClass" = 'CGRStocks'
;
UPDATE offer
SET "isActive" = false
FROM venue_provider
JOIN provider ON provider.id = venue_provider."providerId"
WHERE venue_provider."venueId" = offer."venueId"
  AND provider."localClass" = 'EMSStocks'
;

-- Anonymize redactor for table CollectiveOfferRequest
UPDATE collective_offer_request
SET
    "phoneNumber" =  pg_temp.fake_phone_number_from_id(id);

UPDATE "offerer_invitation"
SET
    "email" = 'user' || "id" || '@anonymized.email'
WHERE email NOT LIKE '%@passculture.app';