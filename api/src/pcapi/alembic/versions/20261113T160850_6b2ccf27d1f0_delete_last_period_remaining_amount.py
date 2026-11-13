"""Delete lastPeriodRemainingAmount from educational_deposit"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6b2ccf27d1f0"
down_revision = "635a4b23fc44"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("educational_deposit", "lastPeriodRemainingAmount")


def downgrade() -> None:
    op.add_column(
        "educational_deposit",
        sa.Column("lastPeriodRemainingAmount", sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    )
