"""create_offer_report_tables

Revision ID: 2f8574b8f1f0
Revises: bb84cb0e65c2
Create Date: 2021-07-03 04:50:44.825877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f8574b8f1f0"
down_revision = "bb84cb0e65c2"
branch_labels = None
depends_on = None


CHECK_CONSTRAINT = """
(offer_report.reason != 'OTHER' AND offer_report.\"customReasonContent\" IS NULL)
OR (
    offer_report.reason = 'OTHER'
    AND offer_report.\"customReasonContent\" IS NOT NULL
    AND trim(both ' ' from offer_report.\"customReasonContent\") != ''
)
"""


def upgrade():
    op.create_table(
        "offer_report",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("reportedAt", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("customReasonContent", sa.Text(), nullable=True),
        sa.CheckConstraint(CHECK_CONSTRAINT, name="custom_reason_null_only_if_reason_is_other"),
        sa.ForeignKeyConstraint(
            ["offerId"],
            ["offer.id"],
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "offerId", name="unique_offer_per_user"),
    )
    op.create_index(op.f("ix_offer_report_offerId"), "offer_report", ["offerId"], unique=False)
    op.create_index(op.f("ix_offer_report_reason"), "offer_report", ["reason"], unique=False)
    op.create_index(op.f("ix_offer_report_userId"), "offer_report", ["userId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_offer_report_userId"), table_name="offer_report")
    op.drop_index(op.f("ix_offer_report_reason"), table_name="offer_report")
    op.drop_index(op.f("ix_offer_report_offerId"), table_name="offer_report")
    op.drop_table("offer_report")
    op.execute("drop type if exists reason")
