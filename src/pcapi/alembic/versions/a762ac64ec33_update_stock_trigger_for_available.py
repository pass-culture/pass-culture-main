"""update_stock_trigger_for_available_changes

Revision ID: a762ac64ec33
Revises: 47576c4aecc3
Create Date: 2019-09-25 13:03:10.212147

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a762ac64ec33'
down_revision = '47576c4aecc3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION save_stock_modification_date()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.available != OLD.available THEN
            NEW."dateModified" = NOW();
          END IF;
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
