"""add_is_synchronization_compatible_product
"""
from alembic import op
import sqlalchemy as sa


revision = "9e5ae228e4ab"
down_revision = "6a3db6c2a7b1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "product",
        sa.Column("isSynchronizationCompatible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )


def downgrade():
    op.drop_column("product", "isSynchronizationCompatible")
