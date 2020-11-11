"""Make offer and product type not null, index them

Revision ID: 8e1f487e2d23
Revises: 2920fd4ec916
Create Date: 2019-07-24 07:51:53.868166

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8e1f487e2d23"
down_revision = "bee8a14c1202"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_offer_type ON offer (type);
        CREATE INDEX IF NOT EXISTS ix_product_type ON product (type);
        ALTER TABLE offer ALTER COLUMN type SET NOT NULL;
        ALTER TABLE product ALTER COLUMN type SET NOT NULL;
        ALTER TABLE offer ADD CONSTRAINT "offer_type_check" CHECK (type::text <> 'None'::text);
        ALTER TABLE product ADD CONSTRAINT "product_type_check" CHECK (type::text <> 'None'::text);
    """
    )


def downgrade():
    op.execute(
        """
      DROP INDEX ix_offer_type;
      DROP INDEX ix_product_type;
      ALTER TABLE offer ALTER COLUMN type DROP NOT NULL;
      ALTER TABLE product ALTER COLUMN type DROP NOT NULL;
      ALTER TABLE offer DROP CONSTRAINT "offer_type_check";
      ALTER TABLE product DROP CONSTRAINT "product_type_check";
    """
    )
