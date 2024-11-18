SET lock_timeout = '5s';

DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_content___ts_vector___ccnew";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_ean_ccnew";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_ean_ccnew1";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_ean_ccnew2";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_ean_ccnew3";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_ean_ccnew4";
DROP INDEX CONCURRENTLY IF EXISTS "ix_chronicle_userId_ccnew";
DROP INDEX CONCURRENTLY IF EXISTS "ix_product_chronicle_chronicleId_ccnew";
DROP INDEX CONCURRENTLY IF EXISTS "ix_product_chronicle_productId_ccnew";

SET lock_timeout = '0';
