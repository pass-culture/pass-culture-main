"""Drop non_payment_notice.batchId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7532a8175314"
down_revision = "ce10822461a5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("non_payment_notice", "batchId")


def downgrade() -> None:
    op.add_column("non_payment_notice", sa.Column("batchId", sa.BIGINT(), autoincrement=False, nullable=True))
