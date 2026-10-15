-- One time script to recreate an index reported as invalid
-- Sentry issue: https://pass-culture.sentry.io/issues/153311252/

DROP INDEX CONCURRENTLY IF EXISTS "ix_fraudulent_booking_tag_venueId";

SET SESSION statement_timeout='900s';
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_fraudulent_booking_tag_venueId" ON public."fraudulent_booking_tag" USING btree ("venueId");
SET SESSION statement_timeout=60000;  -- restore value set in infra/layers/pcapi/deployments/values-default.yaml.gotmpl

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
