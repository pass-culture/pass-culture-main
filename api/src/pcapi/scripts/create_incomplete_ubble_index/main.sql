SET SESSION statement_timeout='300s';

CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_beneficiary_fraud_check_incomplete_ubble 
ON beneficiary_fraud_check (id) 
WHERE status = 'OK'
AND type = 'UBBLE'
AND "eligibilityType" = 'AGE17_18'
AND "thirdPartyId" LIKE 'idv_' || '%%'
AND (("resultContent" ->> 'birth_place') IS NULL
  OR ("resultContent" ->> 'document_issuing_country') IS NULL
  OR ("resultContent" ->> 'nationality') IS NULL);
