"""add triggers to version user

Revision ID: 565f79cfa5b2
Revises: cff9e82d0558
Create Date: 2019-05-28 07:03:16.612332

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '565f79cfa5b2'
down_revision = 'cff9e82d0558'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        CREATE OR REPLACE FUNCTION public.audit_table(target_table regclass, ignored_cols text[])
         RETURNS void
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            stm_targets text = 'INSERT OR UPDATE OR DELETE OR TRUNCATE';
            query text;
            excluded_columns_text text = '';
        BEGIN
            EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_row ON ' || target_table;
        
            IF array_length(ignored_cols, 1) > 0 THEN
                excluded_columns_text = ', ' || quote_literal(ignored_cols);
            END IF;
            query = 'CREATE TRIGGER audit_trigger_row AFTER INSERT OR UPDATE OR DELETE ON ' ||
                     target_table || ' FOR EACH ROW ' ||
                     E'WHEN (current_setting(\\'session_replication_role\\') ' ||
                     E'<> \\'local\\')' ||
                     ' EXECUTE PROCEDURE create_activity(' ||
                     excluded_columns_text ||
                     ');';
            RAISE NOTICE '%', query;
            EXECUTE query;
            stm_targets = 'TRUNCATE';
        END;
        $function$

    ''')
    op.execute('''
    SELECT public.audit_table(oid, ARRAY['password', 'resetPasswordToken', 'validationToken']) 
    FROM pg_class 
    WHERE oid = 'user'::regclass;
    ''')


def downgrade():
    op.execute('''
    DROP TRIGGER audit_trigger_delete ON "user";
    DROP TRIGGER audit_trigger_insert ON "user";
    DROP TRIGGER audit_trigger_update ON "user";
    ''')
