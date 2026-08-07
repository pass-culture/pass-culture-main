"""Add educational_deposit lastPeriodRemainingAmount (to replace remaining_amount, removed in a post migration)"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a703309b6657"
down_revision = "dc178062bf79"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "educational_deposit", sa.Column("lastPeriodRemainingAmount", sa.Numeric(precision=10, scale=2), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("educational_deposit", "lastPeriodRemainingAmount")
