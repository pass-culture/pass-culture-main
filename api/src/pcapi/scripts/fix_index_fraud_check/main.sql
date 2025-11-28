SET SESSION lock_timeout='300s';
SET SESSION statement_timeout='300s';

DROP INDEX CONCURRENTLY IF EXISTS ix_fraud_check_type_initiated_status;
DROP INDEX CONCURRENTLY IF EXISTS ix_beneficiary_fraud_check_type_initiated_status;
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_beneficiary_fraud_check_type_initiated_status ON beneficiary_fraud_check (id, type) WHERE status = 'STARTED' OR status = 'PENDING';
