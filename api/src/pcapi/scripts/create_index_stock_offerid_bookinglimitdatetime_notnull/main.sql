-- One time script to create the index "ix_stock_offerId_bookingLimitDatetime_notnull"

\timing on

SET SESSION statement_timeout = 0;
SET SESSION lock_timeout = 0;
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_stock_offerId_bookingLimitDatetime_notnull" ON public.stock USING btree ("offerId", "bookingLimitDatetime") WHERE (("isSoftDeleted" IS NOT TRUE) AND ("bookingLimitDatetime" IS NOT NULL));
SET SESSION statement_timeout = 60000;  -- restore value
RESET lock_timeout;

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
