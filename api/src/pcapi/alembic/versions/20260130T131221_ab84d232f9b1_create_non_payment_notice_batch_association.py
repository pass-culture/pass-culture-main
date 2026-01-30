"""Create table: non_payment_notice_batch_association"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ab84d232f9b1"
down_revision = "7c1693892cbc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "non_payment_notice_batch_association",
        sa.Column("noticeId", sa.BigInteger(), nullable=False),
        sa.Column("batchId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["batchId"],
            ["cashflow_batch.id"],
        ),
        sa.ForeignKeyConstraint(["noticeId"], ["non_payment_notice.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("noticeId", "batchId", name="unique_non_payment_notice_batch_association"),
    )


def downgrade() -> None:
    op.drop_table("non_payment_notice_batch_association")
