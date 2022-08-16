"""add_cookies_history_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "12adabc7c5d3"
down_revision = "76d1434f787d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cookies_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("addedDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deviceId", sa.String(), nullable=False),
        sa.Column("consent", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actionDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cookies_history_userId"), "cookies_history", ["userId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cookies_history_userId"), table_name="cookies_history")
    op.drop_table("cookies_history")
