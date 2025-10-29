SET statement_timeout = 0;

COMMIT;

CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_venueId_subcategoryId" ON offer ("venueId", "subcategoryId");

SET statement_timeout TO DEFAULT;