-- One time script to recreate an index reported as invalid
-- Sentry issue: https://pass-culture.sentry.io/issues/153311252

DROP INDEX IF EXISTS "ix_favorite_artist_artistId";
DROP INDEX IF EXISTS "ix_favorite_artist_userId";

SET SESSION statement_timeout='900s';
CREATE INDEX IF NOT EXISTS "ix_favorite_artist_artistId" ON public.favorite_artist USING btree ("artistId");
CREATE INDEX IF NOT EXISTS "ix_favorite_artist_userId" ON public.favorite_artist USING btree ("userId");
SET SESSION statement_timeout=60000;  -- restore value set in infra/layers/pcapi/deployments/values-default.yaml.gotmpl

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
