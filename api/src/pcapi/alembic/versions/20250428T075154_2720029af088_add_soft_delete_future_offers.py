"""Add isSoftDeleted column to future_offer model
add_soft_delete_future_offers
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2720029af088"
down_revision = "215ee3f02614"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "future_offer", sa.Column("isSoftDeleted", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("future_offer", "isSoftDeleted")
