CREATE OR REPLACE FUNCTION pg_temp.generate_booking_token_from_id(id BIGINT)
 RETURNS VARCHAR(6) AS $$
BEGIN
 RETURN upper(lpad(to_hex(id), 6, '0'));
END; $$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION pg_temp.random_text(len INT)
 RETURNS TEXT AS $$
BEGIN
 RETURN substring(gen_random_uuid()::text, 1, len);
END; $$
LANGUAGE plpgsql;


UPDATE offerer SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" is not null;

BEGIN;
  -- Temporarily remove trigger to speed up updates.
  DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;
  -- Temporarily set all tokens to NULL to avoiding triggering
  -- UNIQUEness error on existing tokens on the second UPDATE.
  ALTER TABLE booking ALTER COLUMN token DROP NOT NULL;
  UPDATE booking SET token = NULL;
  UPDATE booking SET token = pg_temp.generate_booking_token_from_id(id);
  -- Restore constraints and triggers.
  ALTER TABLE booking ALTER COLUMN token SET NOT NULL;
  CREATE TRIGGER stock_update_cancellation_date
    BEFORE INSERT OR UPDATE ON booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_cancellation_date();
COMMIT;

-- Set fake IBAN and BIC in `bank_information` table...
UPDATE bank_information SET "iban" = 'FR' || lpad(id::text, 25, '0') WHERE "iban" is not null;
UPDATE bank_information SET "bic" = 'XX' || lpad(id::text, 6, '0') WHERE "bic" is not null;
-- ... and reuse them in `payment` table.
UPDATE payment
SET iban = bank_information.iban, bic = bank_information.bic
FROM booking, bank_information
WHERE
  payment.iban IS NOT NULL
  AND booking.id = payment."bookingId"
  AND (
    bank_information."venueId" = booking."venueId"
    OR bank_information."offererId" = booking."offererId"
  )
;

UPDATE activation_code SET code = 'FAKE-' || id::text ;

UPDATE provider SET "authToken" = pg_temp.random_text(32) WHERE "authToken" is not null;

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
    "validationToken" = NULL,
    "resetPasswordToken" = NULL
;

UPDATE user_offerer SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" is not null;


UPDATE venue SET "validationToken" = pg_temp.random_text(27) WHERE "validationToken" is not null;
