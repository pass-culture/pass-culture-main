-- One time script to create the index "ix_offer_venueId_name_id"

\timing on

SET SESSION statement_timeout = 0;
SET SESSION lock_timeout = 0;
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_venueId_name_id" ON public.offer USING btree ("venueId", lower(immutable_unaccent((name)::text)), id DESC);
SET SESSION statement_timeout = 60000;  -- restore value
RESET lock_timeout;

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
