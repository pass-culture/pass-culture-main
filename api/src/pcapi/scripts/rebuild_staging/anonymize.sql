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


UPDATE offerer SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" is not null;

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

UPDATE activation_code SET code = 'FAKE-' || id::text ;

UPDATE provider
SET "authToken" = 'anonymized, you may have to set it if you want to use this provider'
WHERE "authToken" IS NOT NULL
;

UPDATE api_key SET secret = pg_temp.random_text(32)::bytea;

UPDATE "user"
SET
    "email" = 'user@' || "id",
    "publicName" = 'User' || "id",
    "password" = 'fake-hashed-password'::bytea,
    "firstName" = 'firstName' || "id",
    "lastName" = 'lastName' || "id",
    "dateOfBirth" = '01/01/2001',
    "phoneNumber" = '0606060606',
    "validationToken" = NULL
WHERE email NOT LIKE '%@passculture.app';
;

UPDATE "user"
SET
    "password" = 'fake-hashed-password'::bytea,
    "dateOfBirth" = '01/01/2001',
    "phoneNumber" = '0606060606',
    "validationToken" = NULL
WHERE email LIKE '%@passculture.app';
;

UPDATE "user_email_history"
SET
    "oldUserEmail" = 'old_user',
    "oldDomainEmail" = "id",
    "newUserEmail" = 'user',
    "newDomainEmail" = "id"
;

UPDATE user_offerer SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" IS NOT NULL;


UPDATE venue SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" IS NOT NULL;


-- Anonymize beneficiary_fraud_check table content
UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || (
    '{"email": "anonymized@example.com", "address": "42 rue de la ville", "lastName": "lastName' || "userId" || '", "firstName": "firstName' || "userId" || '", "phoneNumber": "+33606060606", "bodyPieceNumber": "000000000000"}'
  )::text::jsonb
WHERE "type" = 'JOUVE'
;

UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || (
    '{"last_name": "lastName' || "userId" || '", "first_name": "firstName' || "userId" || '"}'
  )::text::jsonb
WHERE "type" = 'EDUCONNECT'
;

UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || (
    '{"last_name": "lastName' || "userId" || '", "first_name": "firstName' || "userId" || '", "married_name": "marriedName", "id_document_number": null, "identification_url": null}'
  )::text::jsonb
WHERE "type" = 'UBBLE'
;

UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || (
    '{"email": "anonymized@example.com", "phone": "0606060606", "address": "42 rue de la ville 44000 Nantes", "last_name": "lastName' || "userId" || '", "first_name": "firstName' || "userId" || '", "id_piece_number": "00000000 1 ZZ0"}'
  )::text::jsonb
WHERE "type" = 'DMS'
;

UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || '{"phone_number": "0606060606"}'
WHERE "type" in ('INTERNAL_REVIEW', 'PHONE_VALIDATION')
;

UPDATE beneficiary_fraud_check
SET "resultContent" = "resultContent" || '{"account_email": "anonymized@example.com"}'
WHERE "type" = 'USER_PROFILING'
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

-- Anonymize beneficiary_fraud_review table content
UPDATE beneficiary_fraud_review
SET reason = ''
WHERE reason is not null
;
