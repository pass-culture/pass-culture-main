-- One time script to recreate indexes reported as invalid
-- Sentry issue: https://pass-culture.sentry.io/issues/32062823/events/ba19b71c15a841d89a2a6693a29939e4/?project=4508776981069904
-- Found invalid PostgreSQL indexes:
-- ix_action_history_userProfileRefreshCampaignId
-- ix_address_postalCode
-- ix_address_trgm_unaccent_city
-- ix_collective_booking_educationalDepositId
-- ix_highlight_unaccent_name
-- ix_unique_offerer_address_per_label
-- ix_wip_unique_offerer_address_when_label_is_not_null
-- ix_wip_unique_offerer_address_when_label_is_null

SET SESSION statement_timeout='900s';

DROP INDEX CONCURRENTLY IF EXISTS "ix_action_history_userProfileRefreshCampaignId";
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_action_history_userProfileRefreshCampaignId" ON public."action_history" USING btree ("userProfileRefreshCampaignId") WHERE ("userProfileRefreshCampaignId" IS NOT NULL);

DROP INDEX CONCURRENTLY IF EXISTS "ix_address_postalCode";
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_address_postalCode" ON public."address" USING btree ("postalCode");

DROP INDEX CONCURRENTLY IF EXISTS "ix_address_trgm_unaccent_city";
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_address_trgm_unaccent_city" ON public."address" USING gin (public.immutable_unaccent(city) public.gin_trgm_ops);

DROP INDEX CONCURRENTLY IF EXISTS "ix_collective_booking_educationalDepositId";
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_collective_booking_educationalDepositId" ON public."collective_booking" USING btree ("educationalDepositId");

DROP INDEX CONCURRENTLY IF EXISTS "ix_highlight_unaccent_name";
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_highlight_unaccent_name" ON public."highlight" USING gin (public.immutable_unaccent(name) public.gin_trgm_ops);

DROP INDEX CONCURRENTLY IF EXISTS "ix_unique_offerer_address_per_label";
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_unique_offerer_address_per_label" ON public."offerer_address" USING btree ("offererId", "addressId", label) WHERE ((type IS NULL) AND ("venueId" IS NULL));

DROP INDEX CONCURRENTLY IF EXISTS "ix_wip_unique_offerer_address_when_label_is_not_null";
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_wip_unique_offerer_address_when_label_is_not_null" ON public."offerer_address" USING btree ("offererId", "addressId", "label", "type", "venueId") NULLS NOT DISTINCT WHERE (label IS NOT NULL);

DROP INDEX CONCURRENTLY IF EXISTS "ix_wip_unique_offerer_address_when_label_is_null";
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_wip_unique_offerer_address_when_label_is_null" ON public."offerer_address" USING btree ("offererId", "addressId", "type", "venueId") NULLS NOT DISTINCT WHERE ((label IS NULL) AND ("venueId" IS NOT NULL));

SET SESSION statement_timeout=60000;  -- restore value set in helm/pcapi/production/values-configmaps.yaml:

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
