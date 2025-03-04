SET SESSION statement_timeout='300s';
REINDEX INDEX CONCURRENTLY "ix_educational_institution_department_code";
SET SESSION statement_timeout=60000;  -- restore value set in helm/pcapi/production/values-configmaps.yaml:

-- Print invalid indexes to check in logs that the index is now valid
SELECT relname
FROM pg_class,
    pg_index
WHERE pg_index.indisvalid = false
    AND pg_index.indexrelid = pg_class.oid;
