"""delete_activity_triggers_on_mediation_and_product

Revision ID: 0fc312879579
Revises: 97c9d39f2fa7
Create Date: 2019-12-04 10:02:29.300913

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0fc312879579'
down_revision = '97c9d39f2fa7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DROP TRIGGER IF EXISTS audit_trigger_delete ON product;
        DROP TRIGGER IF EXISTS audit_trigger_insert ON product;
        DROP TRIGGER IF EXISTS audit_trigger_update ON product;
        DROP TRIGGER IF EXISTS audit_trigger_delete ON mediation;
        DROP TRIGGER IF EXISTS audit_trigger_insert ON mediation;
        DROP TRIGGER IF EXISTS audit_trigger_update ON mediation;
    """)


def downgrade():
    op.execute("""
        CREATE TRIGGER audit_trigger_delete 
        AFTER DELETE ON mediation REFERENCING OLD TABLE AS old_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
        
        CREATE TRIGGER audit_trigger_insert 
        AFTER INSERT ON mediation REFERENCING NEW TABLE AS new_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
        
        CREATE TRIGGER audit_trigger_update 
        AFTER UPDATE ON mediation REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
        
        CREATE TRIGGER audit_trigger_delete 
        AFTER DELETE ON product REFERENCING OLD TABLE AS old_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
        
        CREATE TRIGGER audit_trigger_insert 
        AFTER INSERT ON product REFERENCING NEW TABLE AS new_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
        
        CREATE TRIGGER audit_trigger_update 
        AFTER UPDATE ON product REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table 
        FOR EACH STATEMENT WHEN (current_setting('session_replication_role'::text) <> 'local'::text) 
        EXECUTE PROCEDURE create_activity();
    """)
