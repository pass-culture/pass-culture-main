SET
    SESSION statement_timeout = '900s';

DROP INDEX CONCURRENTLY IF EXISTS "ix_pro_advice_venueId";

CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_pro_advice_venueId" ON public."pro_advice" USING btree ("venueId");

-- Restore value set in helm/pcapi/production/values-configmaps.yaml
SET
    SESSION statement_timeout = 60000;

-- Print invalid indexes to check in logs that the index is now valid
SELECT
    relname
FROM
    pg_class,
    pg_index
WHERE
    pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;