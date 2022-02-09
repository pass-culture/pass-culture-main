"""drop_unused_columns_from_models
"""
from alembic import op
import sqlalchemy as sa


revision = "e6b4ede78bb3"
down_revision = "70946e8b0622"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("booking", "isUsed")
    op.drop_column("user", "isAdmin")
    op.drop_column("user", "isBeneficiary")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("isBeneficiary", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
    op.add_column(
        "user", sa.Column("isAdmin", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False)
    )
    op.add_column(
        "booking",
        sa.Column("isUsed", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
