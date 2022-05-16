"""delete_email_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "4f6fd966f8e3"
down_revision = "beaefcf60bc9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("email")
    op.execute("DROP TYPE emailstatus")


def downgrade() -> None:
    op.execute("CREATE TYPE emailstatus AS ENUM('SENT','ERROR')")
    op.create_table(
        "email",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("content", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.Enum("SENT", "ERROR", name="emailstatus"), nullable=False),
        sa.Column("datetime", sa.DateTime(), nullable=False),
    )
