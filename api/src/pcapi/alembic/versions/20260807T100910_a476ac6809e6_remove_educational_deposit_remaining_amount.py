"""Remove educational_deposit remaining_amount (replaced with lastPeriodRemainingAmount)"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a476ac6809e6"
down_revision = "b3e1f2a4c5d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("educational_deposit", "remaining_amount")


def downgrade() -> None:
    op.add_column(
        "educational_deposit",
        sa.Column("remaining_amount", sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    )
