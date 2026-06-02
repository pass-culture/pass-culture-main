SET SESSION lock_timeout = '5s';

REINDEX INDEX CONCURRENTLY "ix_venue_activity";

-- Print invalid indexes to check in logs that the index is now valid
-- if one is _ccnew, this will need to be rerun
SELECT
    relname
FROM
    pg_class,
    pg_index
WHERE
    pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;


DROP INDEX IF EXISTS "ix_venue_activity_ccnew";
DROP INDEX IF EXISTS "ix_venue_activity_ccold";

SET SESSION lock_timeout = 0;

-- Print invalid indexes to check in logs that the index is now valid
SELECT
    relname
FROM
    pg_class,
    pg_index
WHERE
    pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;