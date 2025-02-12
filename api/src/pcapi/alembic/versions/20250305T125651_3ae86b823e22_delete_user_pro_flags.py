"""Delete user_pro_flags table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3ae86b823e22"
down_revision = "dc00a380dc2e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("user_pro_flags")


def downgrade() -> None:
    op.create_table(
        "user_pro_flags",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=True),
        sa.Column("firebase", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        ALTER TABLE user_pro_flags DROP CONSTRAINT IF EXISTS "user_pro_flags_userId_fkey";
        ALTER TABLE user_pro_flags
        ADD CONSTRAINT "user_pro_flags_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user" ("id") ON DELETE CASCADE NOT VALID;
        """
    )
