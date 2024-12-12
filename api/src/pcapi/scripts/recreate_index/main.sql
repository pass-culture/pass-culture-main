-- One time script to recreate an index that is invalid
-- Sentry issue: https://sentry.passculture.team/organizations/sentry/issues/1477809/?project=5
-- DROP
BEGIN;
DROP INDEX IF EXISTS ix_booking_cancellationUserId;
-- CREATE
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_booking_cancellationUserId ON booking USING btree ("cancellationUserId")
WHERE "cancellationUserId" IS NOT NULL;
COMMIT;
-- Print invalid indexes to check in logs that all is a-ok
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;