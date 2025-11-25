SET SESSION statement_timeout='300s';

CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_fraud_check_type_initiated_status ON beneficiary_fraud_check ("eligibilityType") WHERE status IN ('started', 'pending');

SET SESSION statement_timeout=60000;
