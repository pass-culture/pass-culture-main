"""add_constraint_on_stock_on_offer_id

Revision ID: 8388f49ba035
Revises: 37ba62c7fdb3
Create Date: 2019-07-17 13:05:40.502336

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8388f49ba035"
down_revision = "37ba62c7fdb3"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("stock", "offerId", nullable=False)


def downgrade():
    op.alter_column("stock", "offerId", nullable=True)
