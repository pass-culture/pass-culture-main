"""remove-email-table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "820c7bb7f542"
down_revision = "934d0e50595f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("email")
    op.execute("DROP TYPE emailstatus")


def downgrade():
    op.create_table(
        "email",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("content", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.Enum("SENT", "ERROR", name="emailstatus"), nullable=False),
        sa.Column("datetime", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
