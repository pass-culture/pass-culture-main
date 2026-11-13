-- One time script to drop the invalid index "ix_offer_venueId_name_id"

SET SESSION statement_timeout = 0;
SET SESSION lock_timeout = 0;
DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_venueId_name_id";
SET SESSION statement_timeout = 60000;
RESET lock_timeout;
