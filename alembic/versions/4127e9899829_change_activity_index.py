"""change activity index from changed_data ->> id to old_data ->> id

Revision ID: 4127e9899829
Revises: 0df577e35e9f
Create Date: 2019-06-18 08:41:38.228124

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '4127e9899829'
down_revision = '0df577e35e9f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        DROP INDEX IF EXISTS idx_activity_objid;
        CREATE INDEX idx_activity_changed_data 
        ON activity 
        (table_name, CAST((changed_data ->> 'id') AS integer));        
        CREATE INDEX idx_activity_old_data 
        ON activity 
        (table_name, CAST((old_data ->> 'id') AS integer));
        '''
    )


def downgrade():
    op.execute(
        '''
        DROP INDEX IF EXISTS idx_activity_changed_data;
        DROP INDEX IF EXISTS idx_activity_old_data;
        CREATE INDEX idx_activity_objid
        ON activity 
        (CAST((changed_data ->> 'id') AS integer));
        '''
    )
