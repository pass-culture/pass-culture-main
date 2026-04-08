SET SESSION lock_timeout = '5s';
-- REINDEX INDEX CONCURRENTLY "ix_product_mediation_productId_uuid";
DROP INDEX IF EXISTS "ix_product_mediation_productId_uuid_ccnew";
DROP INDEX IF EXISTS "ix_product_mediation_productId_uuid_ccnew1";
-- DROP INDEX IF EXISTS xo_ix_image_type;
-- CREATE INDEX CONCURRENTLY xo_ix_image_type ON product_mediation ("imageType") INCLUDE ("productId");
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
