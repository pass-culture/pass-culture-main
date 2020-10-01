CREATE OR REPLACE FUNCTION ${schema_prefix}create_activity() RETURNS TRIGGER AS $$
DECLARE
    audit_row ${schema_prefix}activity;
    excluded_cols text[] = ARRAY[]::text[];
BEGIN
    audit_row.id = nextval('${schema_prefix}activity_id_seq');
    audit_row.schema_name = TG_TABLE_SCHEMA::text;
    audit_row.table_name = TG_TABLE_NAME::text;
    audit_row.relid = TG_RELID;
    audit_row.issued_at = statement_timestamp() AT TIME ZONE 'UTC';
    audit_row.native_transaction_id = txid_current();
    audit_row.transaction_id = (
        SELECT id
        FROM ${schema_prefix}transaction
        WHERE
            native_transaction_id = txid_current() AND
            issued_at >= (NOW() - INTERVAL '1 day')
        ORDER BY issued_at DESC
        LIMIT 1
    );
    audit_row.verb = LOWER(TG_OP);
    audit_row.old_data = '{}'::jsonb;
    audit_row.changed_data = '{}'::jsonb;

    IF TG_ARGV[0] IS NOT NULL THEN
        excluded_cols = TG_ARGV[0]::text[];
    END IF;

    IF (TG_OP = 'UPDATE' AND TG_LEVEL = 'ROW') THEN
        audit_row.old_data = row_to_json(OLD.*)::jsonb - excluded_cols;
        audit_row.changed_data = (
            row_to_json(NEW.*)::jsonb - audit_row.old_data - excluded_cols
        );
        IF audit_row.changed_data = '{}'::jsonb THEN
            -- All changed fields are ignored. Skip this update.
            RETURN NULL;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_LEVEL = 'ROW') THEN
        audit_row.old_data = row_to_json(OLD.*)::jsonb - excluded_cols;
    ELSIF (TG_OP = 'INSERT' AND TG_LEVEL = 'ROW') THEN
        audit_row.changed_data = row_to_json(NEW.*)::jsonb - excluded_cols;
    END IF;
    INSERT INTO ${schema_prefix}activity VALUES (audit_row.*);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;
