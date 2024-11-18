SET lock_timeout = '5s';

-- chronicle
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_chronicle_content___ts_vector__ ON chronicle USING gin (__content_ts_vector__);
-- REINDEX INDEX CONCURRENTLY ix_chronicle_content___ts_vector__;
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_chronicle_ean ON chronicle (ean);
REINDEX INDEX CONCURRENTLY ix_chronicle_ean;
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_chronicle_userId" ON chronicle ("userId");
-- REINDEX INDEX CONCURRENTLY "ix_chronicle_userId";

-- product_chronicle
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_product_chronicle_chronicleId" ON product_chronicle ("chronicleId");
-- REINDEX INDEX CONCURRENTLY "ix_product_chronicle_chronicleId";
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_product_chronicle_productId" ON product_chronicle ("productId");
-- REINDEX INDEX CONCURRENTLY "ix_product_chronicle_productId";

-- offer_chronicle
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_chronicle_chronicleId" ON offer_chronicle ("chronicleId");
-- REINDEX INDEX CONCURRENTLY "ix_offer_chronicle_chronicleId";
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_chronicle_offerId" ON offer_chronicle ("offerId");

SET lock_timeout = '0';
