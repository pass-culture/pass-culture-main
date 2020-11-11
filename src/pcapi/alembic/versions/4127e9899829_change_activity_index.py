"""add activity index on old_data ->> id

Revision ID: 4127e9899829
Revises: 83132c357143
Create Date: 2019-06-18 08:41:38.228124

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "4127e9899829"
down_revision = "83132c357143"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP INDEX IF EXISTS idx_activity_objid;
        CREATE INDEX idx_activity_changed_data 
        ON activity 
        (table_name, CAST((changed_data ->> 'id') AS integer));        
        CREATE INDEX idx_activity_old_data 
        ON activity 
        (table_name, CAST((old_data ->> 'id') AS integer));
        """
    )
    op.execute("ALTER TABLE activity ALTER COLUMN id SET DEFAULT nextval('activity_id_seq'::regclass);")


def downgrade():
    op.execute(
        """
        DROP INDEX IF EXISTS idx_activity_changed_data;
        DROP INDEX IF EXISTS idx_activity_old_data;
        CREATE INDEX idx_activity_objid
        ON activity 
        (CAST((changed_data ->> 'id') AS integer));
        """
    )
    op.execute("ALTER TABLE activity ALTER COLUMN id SET DEFAULT NONE;")
