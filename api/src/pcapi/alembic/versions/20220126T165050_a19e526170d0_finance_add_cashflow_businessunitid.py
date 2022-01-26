"""Add cashflow.businessUnitId (nullable)"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a19e526170d0"
down_revision = "eb6c7fc2d56f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("cashflow", sa.Column("businessUnitId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_cashflow_businessUnitId"), "cashflow", ["businessUnitId"], unique=False)
    op.create_foreign_key(None, "cashflow", "business_unit", ["businessUnitId"], ["id"])


def downgrade():
    op.drop_column("cashflow", "businessUnitId")
