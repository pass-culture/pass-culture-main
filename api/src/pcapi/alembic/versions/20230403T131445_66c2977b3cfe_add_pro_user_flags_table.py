"""Add user_pro_flags table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "66c2977b3cfe"
down_revision = "1b9fe434199c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_pro_flags",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=True),
        sa.Column("firebase", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_pro_flags")
