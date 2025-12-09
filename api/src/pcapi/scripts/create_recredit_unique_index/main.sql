SET SESSION lock_timeout = '300s';
SET SESSION statement_timeout = '300s';

DROP INDEX IF EXISTS ix_unique_deposit_recredit_type_ccnew;
REINDEX INDEX CONCURRENTLY ix_unique_deposit_recredit_type;
