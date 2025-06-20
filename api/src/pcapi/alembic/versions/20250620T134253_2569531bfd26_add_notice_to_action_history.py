"""Add notice to ActionHistory"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2569531bfd26"
down_revision = "62d5ff24ee22"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("action_history", sa.Column("noticeId", sa.BigInteger(), nullable=True))
    op.create_index(
        "ix_action_history_noticeId",
        "action_history",
        ["noticeId"],
        unique=False,
        postgresql_where=sa.text('"noticeId" IS NOT NULL'),
    )
    op.create_foreign_key(
        "action_history_noticeId_fkey",
        "action_history",
        "non_payment_notice",
        ["noticeId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.create_index(
        "ix_action_history_noticeId",
        "action_history",
        ["noticeId"],
        unique=False,
        postgresql_where=sa.text('"noticeId" IS NOT NULL'),
        if_not_exists=True,
        postgresql_concurrently=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        "ix_action_history_noticeId",
        table_name="action_history",
        postgresql_where=sa.text('"noticeId" IS NOT NULL'),
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
    op.drop_constraint("action_history_noticeId_fkey", "action_history", type_="foreignkey")
    op.drop_column("action_history", "noticeId")
