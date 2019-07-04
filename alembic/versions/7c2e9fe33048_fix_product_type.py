"""fix_product_type

Revision ID: 7c2e9fe33048
Revises: 035f0ee8ea70
Create Date: 2019-07-01 08:10:14.195374

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7c2e9fe33048'
down_revision = '035f0ee8ea70'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
          UPDATE product
          SET type = 'ThingType.' || product.type
          WHERE product.type NOT ILIKE 'ThingType.%'
          AND product."lastProviderId" is not null
    """)


def downgrade():
    pass
