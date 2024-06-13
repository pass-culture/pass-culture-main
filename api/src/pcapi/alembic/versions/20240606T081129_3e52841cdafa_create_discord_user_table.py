"""
create discord_user table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3e52841cdafa"
down_revision = "d43d711e5f8a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discord_user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("discordId", sa.Text(), nullable=True),
        sa.Column("hasAccess", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("isBanned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("lastUpdated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
            name="discord_user_userId_fkey",
            ondelete="CASCADE",
            postgresql_not_valid=True,
        ),
        sa.PrimaryKeyConstraint("id", "userId"),
        sa.UniqueConstraint("discordId"),
    )


def downgrade() -> None:
    op.drop_table("discord_user")
