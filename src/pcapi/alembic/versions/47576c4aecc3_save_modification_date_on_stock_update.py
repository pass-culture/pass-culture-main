"""save_modification_date_on_stock_update

Revision ID: 47576c4aecc3
Revises: 6c67573ad14f
Create Date: 2019-09-13 15:00:46.782915

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '47576c4aecc3'
down_revision = '6c67573ad14f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION save_stock_modification_date()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW."dateModified" = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS stock_update_modification_date ON stock;
        
        CREATE TRIGGER stock_update_modification_date
        BEFORE UPDATE ON stock
        FOR EACH ROW
        EXECUTE PROCEDURE save_stock_modification_date()
        """ + ';')


def downgrade():
    op.execute(
        """
        DROP TRIGGER IF EXISTS stock_update_modification_date ON stock;
        DROP FUNCTION IF EXISTS save_stock_modification_date;
        """
    )
