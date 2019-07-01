"""fix_product_type

Revision ID: 7c2e9fe33048
Revises: d4c38884d642
Create Date: 2019-07-01 08:10:14.195374

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7c2e9fe33048'
down_revision = 'd4c38884d642'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""UPDATE product SET type = 'ThingType.' || product.type WHERE "lastProviderId" in (
        SELECT id FROM provider WHERE "localClass" = 'InitTiteLiveThings'
         OR "localClass" = 'TiteLiveThings'
         AND product.type NOT ILIKE 'ThingType.%'
    )""")


def downgrade():
    pass
