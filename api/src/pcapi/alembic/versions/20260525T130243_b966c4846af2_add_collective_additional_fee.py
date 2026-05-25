"""Add collective_additional_fee table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.educational.models import CollectiveAdditionalFeeType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b966c4846af2"
down_revision = "918cacd4d37d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "collective_additional_fee",
        sa.Column("collectiveStockId", sa.BigInteger(), nullable=False),
        sa.Column("type", MagicEnum(CollectiveAdditionalFeeType), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["collectiveStockId"],
            ["collective_stock.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_collective_additional_fee_collectiveStockId"),
        "collective_additional_fee",
        ["collectiveStockId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("collective_additional_fee")
