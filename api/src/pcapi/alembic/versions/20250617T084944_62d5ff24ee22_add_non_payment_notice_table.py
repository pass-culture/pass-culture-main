"""Add NonPaymentNotice table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers import models as offerers_models
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "62d5ff24ee22"
down_revision = "7f09c1098956"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "non_payment_notice",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("batchId", sa.BigInteger(), nullable=True),
        sa.Column("dateReceived", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("emitterName", sa.Text(), nullable=False),
        sa.Column("emitterEmail", sa.Text(), nullable=False),
        sa.Column("motivation", MagicEnum(offerers_models.NoticeStatusMotivation), nullable=True),
        sa.Column("noticeType", MagicEnum(offerers_models.NoticeType), nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("status", MagicEnum(offerers_models.NoticeStatus), server_default="CREATED", nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "non_payment_notice_batchId_fkey",
        "non_payment_notice",
        "cashflow_batch",
        ["batchId"],
        ["id"],
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "non_payment_notice_offererId_fkey",
        "non_payment_notice",
        "offerer",
        ["offererId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "non_payment_notice_venueId_fkey",
        "non_payment_notice",
        "venue",
        ["venueId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )
    op.create_index(op.f("ix_non_payment_notice_batchId"), "non_payment_notice", ["batchId"], unique=False)
    op.create_index(op.f("ix_non_payment_notice_offererId"), "non_payment_notice", ["offererId"], unique=False)
    op.create_index(op.f("ix_non_payment_notice_venueId"), "non_payment_notice", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_table("non_payment_notice")
