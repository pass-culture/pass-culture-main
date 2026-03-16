CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_venueId_publicationDatetime" ON public.offer USING btree ("venueId", "publicationDatetime")
WHERE
    ("publicationDatetime" IS NOT NULL);