"""create_action_history_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "246156d69d6f"
down_revision = "b5d775ddec23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "action_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("jsonData", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("actionType", sa.Text(), nullable=False),
        sa.Column("actionDate", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("authorUserId", sa.BigInteger(), nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.Column("offererId", sa.BigInteger(), nullable=True),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint('num_nonnulls("userId", "offererId", "venueId") >= 1', name="check_at_least_one_resource"),
        sa.ForeignKeyConstraint(["authorUserId"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_action_history_offererId"), "action_history", ["offererId"], unique=False)
    op.create_index(op.f("ix_action_history_userId"), "action_history", ["userId"], unique=False)
    op.create_index(op.f("ix_action_history_venueId"), "action_history", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_action_history_venueId"), table_name="action_history")
    op.drop_index(op.f("ix_action_history_userId"), table_name="action_history")
    op.drop_index(op.f("ix_action_history_offererId"), table_name="action_history")
    op.drop_table("action_history")
