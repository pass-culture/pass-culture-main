-- One time script to recreate an index that is invalid
-- Sentry issue: https://sentry.passculture.team/organizations/sentry/issues/1477809/?project=5
-- DROP
DROP INDEX CONCURRENTLY IF EXISTS ix_booking_cancellationUserid;
DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_cancellationUserId";
-- CREATE
SET SESSION statement_timeout='900s';
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_cancellationUserId" ON booking USING btree ("cancellationUserId")
WHERE "cancellationUserId" IS NOT NULL;
SET SESSION statement_timeout=60000;  -- restore value set in helm/pcapi/production/values-configmaps.yaml
-- Print invalid indexes to check in logs that all is a-ok
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;