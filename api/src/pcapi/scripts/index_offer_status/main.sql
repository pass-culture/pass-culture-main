CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_venueId_validation_publicationDatetime"
ON public.offer
USING btree ("venueId", "validation", "publicationDatetime");