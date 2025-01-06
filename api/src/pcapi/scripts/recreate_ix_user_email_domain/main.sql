-- One time script to recreate an index reported as invalid
-- Sentry issue: https://sentry.passculture.team/organizations/sentry/issues/1477809/?environment=production&project=5

DROP INDEX CONCURRENTLY IF EXISTS "ix_user_email_domain";

SET SESSION statement_timeout='300s';
CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_user_email_domain" ON public."user" USING btree (email_domain(email));
SET SESSION statement_timeout=60000;  -- restore value set in helm/pcapi/production/values-configmaps.yaml:

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
