"""Add foreign key on product.owningOffererId (Step 2/2)

Revision ID: aa3691cfdc6d
Revises: e8ba63242789
Create Date: 2021-01-27 16:57:14.484948

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "aa3691cfdc6d"
down_revision = "e8ba63242789"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE product VALIDATE CONSTRAINT product_owning_offerer_id_fkey")


def downgrade():
    pass
