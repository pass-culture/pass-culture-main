CREATE EXTENSION pgcrypto;

UPDATE booking SET "token" = substring(md5(random()::text),1 , 6) WHERE "token" is not null;
UPDATE deposit SET "amount" = random() WHERE "amount" is not null;
UPDATE mediation SET "credit" = 'credit text' WHERE "credit" is not null;
UPDATE offer SET "bookingEmail" = 'ano@nym.ized' WHERE "bookingEmail" is not null;
UPDATE offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE offerer SET "name" = 'offerer_' || "id";
UPDATE offerer SET "siren" = trunc(random() * (999999999-100000000+1) + 100000000)::int WHERE "siren" is not null;
UPDATE offerer SET "address" = md5(random()::text),
  "postalCode" = floor(random() * (99999-10000+1) + 10000)::int,
  "city" = md5(random()::text) WHERE "address" is not null;
UPDATE offerer SET "iban" = trunc(random() * (999999999-100000000+1) + 100000000)::int WHERE "iban" is not null;
UPDATE offerer SET "bic" = trunc(random() * (999999999-100000000+1) + 100000000)::int WHERE "bic" is not null;

UPDATE payment SET "recipientName" = 'recipient_name';
UPDATE payment SET "iban" = trunc(random() * (999999999-100000000+1) + 100000000)::int;
UPDATE payment SET "bic" = trunc(random() * (999999999-100000000+1) + 100000000)::int;
UPDATE payment SET "amount" = 1 WHERE "amount" > 0;
UPDATE payment SET "recipientSiren" = trunc(random() * (999999999-100000000+1) + 100000000)::int WHERE "recipientSiren" is not null;
UPDATE payment SET "reimbursementRate" = trunc(random() * (9 - 1 + 1) + 1)::int WHERE "recipientSiren" is not null;

UPDATE payment_status SET "detail" = 'detail for PaymentStatus';

UPDATE provider SET "apiKey" = md5(random()::text) WHERE "apiKey" is not null;

UPDATE "user" SET "email" = 'user_' || "id",
  "publicName" = 'User' || "id",
  "firstName" = 'firstName' || "id",
  "lastName" = 'lastName' || "id",
  "dateOfBirth" = '01/01/1900',
  "phoneNumber" = '0606060606';
UPDATE "user" set "password" = crypt(('##PASSWORD##' || "id"), gen_salt('bf'))::bytea;
UPDATE "user" SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;
UPDATE "user" SET "resetPasswordToken" = substring(md5(random()::text),1 , 10) WHERE "resetPasswordToken" is not null;

UPDATE stock SET "price" = 1 WHERE "price" > 0;

UPDATE user_offerer SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

UPDATE venue SET "name" = 'Venue' || "id",
  "address" = md5(random()::text),
  "latitude" = trunc(random() * (9 - 1 + 1) + 1)::int,
  "longitude" = trunc(random() * (9 - 1 + 1) + 1)::int,
  "postalCode" = floor(random() * (99999-10000+1) + 10000)::int,
  "city" = md5(random()::text) WHERE "address" is not null;
UPDATE venue SET "siret" = trunc(random() * (99999999999999-10000000000000+1) + 10000000000000)::BIGINT WHERE "siret" is not null;
UPDATE venue SET "bookingEmail" = 'ano@nym.ized' WHERE "bookingEmail" is not null;
UPDATE venue SET "iban" = trunc(random() * (999999999-100000000+1) + 100000000)::int;
UPDATE venue SET "bic" = trunc(random() * (999999999-100000000+1) + 100000000)::int;
UPDATE venue SET "comment" = 'comment for venue' WHERE "comment" is not null;
UPDATE venue SET "validationToken" = substring(md5(random()::text),1 , 27) WHERE "validationToken" is not null;

DROP EXTENSION pgcrypto;
