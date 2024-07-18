DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_subcategoryid_hash";
CREATE INDEX IF NOT EXISTS "ix_offer_subcategoryId_hash" ON public.offer USING HASH ("subcategoryId");