"""Add column: non_payment_notice.fees"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ce10822461a5"
down_revision = "54de74fd92f8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("non_payment_notice", sa.Column("fees", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column("non_payment_notice", "fees")
