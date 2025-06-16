-- The same Ubble application has been inserted twice in the database, with same information, at the same date and time.
-- Delete one of them so that it does no longer crash in archive_ubble_user_id_pictures.
-- Sentry: https://pass-culture.sentry.io/issues/35659726/

SELECT id, "dateCreated", "userId", type, "thirdPartyId" FROM beneficiary_fraud_check
WHERE "thirdPartyId" = 'idv_01jm7r7c9mw7wqf4pvhn3e17ah';

DELETE FROM beneficiary_fraud_check
WHERE id = 25397806
AND "thirdPartyId" = 'idv_01jm7r7c9mw7wqf4pvhn3e17ah';

SELECT id, "dateCreated", "userId", type, "thirdPartyId" FROM beneficiary_fraud_check
WHERE "thirdPartyId" = 'idv_01jm7r7c9mw7wqf4pvhn3e17ah';
