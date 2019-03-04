CREATE EXTENSION pgcrypto;

CREATE OR REPLACE FUNCTION pg_temp.generate_random_between(
  upper_limit NUMERIC,
  lower_limit NUMERIC)
  RETURNS NUMERIC AS $$
BEGIN
  RETURN trunc(random() * (upper_limit-lower_limit+1) + lower_limit);
END; $$
LANGUAGE plpgsql;

UPDATE deposit SET "amount" = 500 WHERE "amount" is not null;
UPDATE mediation SET "credit" = 'credit text' WHERE "credit" is not null;
UPDATE offer SET "bookingEmail" = 'ano@nym.ized' WHERE "bookingEmail" is not null;
UPDATE offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE offerer SET "name" = 'offerer_' || "id";
UPDATE offerer SET "siren" = pg_temp.generate_random_between(999999999,100000000)::text WHERE "siren" is not null;
UPDATE offerer SET "address" = '1 Avenue de la Libération',
  "postalCode" = substring("postalCode",1,2) || pg_temp.generate_random_between(999,100)::text,
  "city" = 'Cultureville' WHERE "address" is not null;

UPDATE booking SET "token" = substring(md5(random()::text),1 , 6) WHERE "token" is not null;

UPDATE payment SET "recipientName" = 'recipient_name';
UPDATE payment SET "iban" = pg_temp.generate_random_between(999999999,100000000)::text,
  "bic" = pg_temp.generate_random_between(999999999,100000000)::text WHERE "iban" is not null;
UPDATE payment SET "amount" = 1 WHERE "amount" > 0;
UPDATE payment SET "recipientSiren" = pg_temp.generate_random_between(999999999,100000000)::text WHERE "recipientSiren" is not null;

UPDATE payment_status SET "detail" = 'detail for PaymentStatus';

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

UPDATE bank_information SET "iban" = pg_temp.generate_random_between(999999999,100000000)::text,
  "bic" = pg_temp.generate_random_between(999999999,100000000)::text  WHERE "iban" is not null;

UPDATE venue SET "name" = 'Venue' || "id",
  "bookingEmail" = 'ano@nym.ized',
  "address" = '1 Avenue de la Libération',
  "latitude" = pg_temp.generate_random_between(9,1)::int,
  "longitude" = pg_temp.generate_random_between(9,1)::int,
  "postalCode" = substring("postalCode",1,2) || pg_temp.generate_random_between(999,100)::text,
  "city" = 'Cultureville' WHERE "address" is not null;

UPDATE venue SET siret = offerer.siren || pg_temp.generate_random_between(99999,10000)::text
FROM offerer
WHERE venue."managingOffererId" = offerer.id
AND venue.siret is not null;

UPDATE venue SET "comment" = 'comment for venue' WHERE "comment" is not null;
UPDATE venue SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

DROP EXTENSION pgcrypto;
