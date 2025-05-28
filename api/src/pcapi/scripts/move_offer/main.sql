COMMIT;
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_booking_stockId_hash ON booking USING hash ("stockId");
