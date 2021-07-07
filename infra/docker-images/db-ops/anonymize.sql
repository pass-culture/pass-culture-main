CREATE EXTENSION pgcrypto;

CREATE OR REPLACE FUNCTION pg_temp.generate_random_between(
  upper_limit NUMERIC,
  lower_limit NUMERIC)
  RETURNS NUMERIC AS $$
BEGIN
  RETURN trunc(random() * (upper_limit-lower_limit+1) + lower_limit);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.generate_random_token_if_not_null(
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

CREATE OR REPLACE FUNCTION pg_temp.generate_booking_token_from_id(
 id BIGINT)
 RETURNS VARCHAR(6) AS $$
BEGIN
 RETURN UPPER(RIGHT(int8send(id)::text, 6));
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_json_field(
 json_data JSONB,
 field_name VARCHAR,
 value_for_replace VARCHAR
 )
 RETURNS JSONB as $$
BEGIN
 IF json_data::jsonb ->> field_name IS NOT NULL THEN
  RETURN ((json_data::jsonb
   - field_name::text)::jsonb
   || ('{"' || field_name || '": "' || value_for_replace::text || '"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_validation_token_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 IF json_data::jsonb ->> 'validationToken' IS NOT NULL THEN
  RETURN ((json_data::jsonb
   - 'validationToken'::text)::jsonb
   || ('{"validationToken": "' || pg_temp.generate_random_token_if_not_null(json_data::jsonb ->> 'validationToken') || '"}')::jsonb);
 ELSE
  RETURN json_data;
 END IF;
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_booking_token_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 new_token VARCHAR(6) := pg_temp.generate_booking_token_from_id((json_data::jsonb ->> 'id')::int);
BEGIN
 RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'token', new_token);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_bic_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
 RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'bic', 'BDFEFR2L');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_email_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 user_id TEXT := json_data::jsonb ->> 'id';
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'email', 'user@' || user_id);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_first_name_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 user_id TEXT := json_data::jsonb ->> 'id';
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'firstName', 'firstName' || user_id);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_public_name_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 user_id TEXT := json_data::jsonb ->> 'id';
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'publicName', 'User' || user_id);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_last_name_field(
 json_data JSONB)
 RETURNS JSONB as $$
DECLARE
 user_id TEXT := json_data::jsonb ->> 'id';
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'lastName', 'lastName' || user_id);
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_date_of_birth_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'dateOfBirth', '01/01/2001');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.anonymize_phone_number_field(
 json_data JSONB)
 RETURNS JSONB as $$
BEGIN
  RETURN pg_temp.anonymize_json_field(json_data::jsonb, 'phoneNumber', '0606060606');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.disable_activity_trigger(table_name text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    query text;
BEGIN
    EXECUTE 'ALTER TABLE ' || table_name || ' DISABLE TRIGGER audit_trigger_delete;';
    EXECUTE 'ALTER TABLE ' || table_name || ' DISABLE TRIGGER audit_trigger_insert;';
    EXECUTE 'ALTER TABLE ' || table_name || ' DISABLE TRIGGER audit_trigger_update;';
END;
$function$;

CREATE OR REPLACE FUNCTION pg_temp.enable_activity_trigger(table_name text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    query text;
BEGIN
    EXECUTE 'ALTER TABLE ' || table_name || ' ENABLE TRIGGER audit_trigger_delete;';
    EXECUTE 'ALTER TABLE ' || table_name || ' ENABLE TRIGGER audit_trigger_insert;';
    EXECUTE 'ALTER TABLE ' || table_name || ' ENABLE TRIGGER audit_trigger_update;';
END;
$function$;

ALTER TABLE "user" DISABLE TRIGGER audit_trigger_insert;
ALTER TABLE "user" DISABLE TRIGGER audit_trigger_update;
ALTER TABLE "user" DISABLE TRIGGER audit_trigger_delete;

SELECT pg_temp.disable_activity_trigger('offerer');
SELECT pg_temp.disable_activity_trigger('venue');
SELECT pg_temp.disable_activity_trigger('booking');
SELECT pg_temp.disable_activity_trigger('stock');
SELECT pg_temp.disable_activity_trigger('bank_information');
SELECT pg_temp.disable_activity_trigger('mediation');
SELECT pg_temp.disable_activity_trigger('offer');
SELECT pg_temp.disable_activity_trigger('product');
SELECT pg_temp.disable_activity_trigger('venue_provider');

UPDATE offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

UPDATE booking SET "token" = pg_temp.generate_booking_token_from_id("id") WHERE "token" is not null;

UPDATE payment SET "iban" = 'FR7630001007941234567890185' WHERE "iban" is not null;
UPDATE payment SET "bic" = 'BDFEFR2L' WHERE "bic" is not null;

UPDATE provider SET "apiKey" = substring(md5(random()::text), 1, 32) WHERE "apiKey" is not null;

UPDATE "user" SET "email" = 'user@' || "id",
  "publicName" = 'User' || "id",
  "password" = crypt(('##PASSWORD##' || "id"), gen_salt('bf'))::bytea;
UPDATE "user" SET  "firstName" = 'firstName' || "id" WHERE "firstName" IS NOT NULL;
UPDATE "user" SET "lastName" = 'lastName' || "id" WHERE "lastName" IS NOT NULL;
UPDATE "user" SET "dateOfBirth" = '01/01/2001' WHERE "dateOfBirth" IS NOT NULL;
UPDATE "user" SET "phoneNumber" = '0606060606' WHERE "phoneNumber" IS NOT NULL;
UPDATE "user" SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE "user" SET "resetPasswordToken" = substring(md5(random()::text),1 , 10) WHERE "resetPasswordToken" is not null;

UPDATE user_offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

UPDATE venue SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

SELECT pg_temp.enable_activity_trigger('offerer');
SELECT pg_temp.enable_activity_trigger('venue');
SELECT pg_temp.enable_activity_trigger('booking');
SELECT pg_temp.enable_activity_trigger('stock');
SELECT pg_temp.enable_activity_trigger('bank_information');
SELECT pg_temp.enable_activity_trigger('mediation');
SELECT pg_temp.enable_activity_trigger('offer');
SELECT pg_temp.enable_activity_trigger('product');
SELECT pg_temp.enable_activity_trigger('venue_provider');

ALTER TABLE "user" ENABLE TRIGGER audit_trigger_insert;
ALTER TABLE "user" ENABLE TRIGGER audit_trigger_update;
ALTER TABLE "user" ENABLE TRIGGER audit_trigger_delete;

DROP EXTENSION pgcrypto;
