CREATE EXTENSION pgcrypto;

CREATE OR REPLACE FUNCTION pg_temp.generate_random_between(
  upper_limit NUMERIC,
  lower_limit NUMERIC)
  RETURNS NUMERIC AS $$
BEGIN
  RETURN trunc(random() * (upper_limit-lower_limit+1) + lower_limit);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_random_token_if_not_null(
  original_token VARCHAR)
  RETURNS VARCHAR AS $$
BEGIN
 IF original_token IS NOT NULL THEN
  RETURN substring(md5(random()::text),1 , LENGTH(original_token));
 ELSE
  RETURN NULL;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_token_from_id(
 id BIGINT)
 RETURNS VARCHAR(6) AS $$
BEGIN
 RETURN UPPER(RIGHT(int8send(id)::text, 6));
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_validation_token_field(
 json_data JSONB)
 RETURNS JSONB as $$

BEGIN
 IF json_data::jsonb ->> 'validationToken' IS NOT NULL THEN
  RETURN ((json_data::jsonb
   - 'validationToken'::text)::jsonb
   || ('{"validationToken": "' || generate_random_token_if_not_null(json_data::jsonb ->> 'validationToken') || '"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_token_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 new_token VARCHAR(6) := generate_token_from_id((json_data::jsonb ->> 'id')::int);
BEGIN
 IF json_data::jsonb ->> 'token' IS NOT NULL THEN
  RETURN ((json_data::jsonb - 'token'::text)::jsonb
   || ('{"token": "' || new_token || '"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_booking_email_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 IF json_data ->> 'bookingEmail' IS NOT NULL THEN
  RETURN ((json_data::jsonb
   - 'bookingEmail'::text)::jsonb
   || ('{"bookingEmail": "ano@nym.ized"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_bic_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 IF json_data ->> 'bic' IS NOT NULL THEN
  RETURN ((json_data::jsonb
  - 'bic'::text)::jsonb
|| ('{"bic": "BDFEFR2L"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_iban_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 IF json_data ->> 'iban' IS NOT NULL THEN
  RETURN ((json_data::jsonb
  - 'iban'::text)::jsonb
  || ('{"iban": "FR7630001007941234567890185"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION anonymize_activity_data_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 json_data = anonymize_validation_token_field(json_data::jsonb);
 json_data = anonymize_token_field(json_data::jsonb);
 json_data = anonymize_booking_email_field(json_data::jsonb);
 json_data = anonymize_bic_field(json_data::jsonb);
 json_data = anonymize_iban_field(json_data::jsonb);
 RETURN json_data;
END; $$
LANGUAGE plpgsql;

UPDATE offer SET "bookingEmail" = 'ano@nym.ized' WHERE "bookingEmail" is not null;
UPDATE offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE bank_information SET "iban" = pg_temp.generate_random_between(999999999,100000000)::text,
  "bic" = pg_temp.generate_random_between(999999999,100000000)::text WHERE "iban" is not null;
UPDATE booking SET "token" = generate_token_from_id("id") WHERE "token" is not null;

UPDATE payment SET "iban" = 'FR7630001007941234567890185',
  "bic" = 'BDFEFR2L' WHERE "iban" is not null;

UPDATE provider SET "apiKey" = md5(random()::text) WHERE "apiKey" is not null;

UPDATE "user" SET "email" = 'user@' || "id",
  "publicName" = 'User' || "id",
  "firstName" = 'firstName' || "id",
  "lastName" = 'lastName' || "id",
  "dateOfBirth" = '01/01/2001',
  "phoneNumber" = '0606060606',
  "password" = crypt(('##PASSWORD##' || "id"), gen_salt('bf'))::bytea;
UPDATE "user" SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE "user" SET "resetPasswordToken" = substring(md5(random()::text),1 , 10) WHERE "resetPasswordToken" is not null;

UPDATE user_offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

UPDATE bank_information SET "iban" = 'FR7630001007941234567890185',
  "bic" = 'BDFEFR2L'  WHERE "iban" is not null;

UPDATE venue SET "bookingEmail" = 'ano@nym.ized',
 "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

UPDATE activity
SET
 old_data = anonymize_activity_data_field(old_data),
 changed_data = anonymize_activity_data_field(changed_data);

TRUNCATE email;

DROP EXTENSION pgcrypto;
