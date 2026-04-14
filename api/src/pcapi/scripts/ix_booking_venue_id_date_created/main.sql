SET statement_timeout = 0;

COMMIT;

CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_venueId_dateCreated" ON booking ("venueId", "dateCreated");

SET statement_timeout TO DEFAULT;
