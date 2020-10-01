CREATE OR REPLACE FUNCTION
${schema_prefix}audit_table(target_table regclass, ignored_cols text[])
RETURNS void AS $$
DECLARE
    query text;
    excluded_columns_text text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_insert ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_update ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_delete ON ' || target_table;

    IF array_length(ignored_cols, 1) > 0 THEN
        excluded_columns_text = ', ' || quote_literal(ignored_cols);
    END IF;
    query = 'CREATE TRIGGER audit_trigger_insert AFTER INSERT ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE ${schema_prefix}create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_update AFTER UPDATE ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE ${schema_prefix}create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_delete AFTER DELETE ON ' ||
             target_table || ' REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE ${schema_prefix}create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
END;
$$
language 'plpgsql';


CREATE OR REPLACE FUNCTION ${schema_prefix}audit_table(target_table regclass) RETURNS void AS $$
SELECT ${schema_prefix}audit_table(target_table, ARRAY[]::text[]);
$$ LANGUAGE SQL;
