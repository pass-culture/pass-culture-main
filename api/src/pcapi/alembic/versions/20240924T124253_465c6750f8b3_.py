"""
Create achievements table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "465c6750f8b3"
down_revision = "c3ae9b34287c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "achievement",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_achievement",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("achievementId", sa.Integer(), nullable=False),
        sa.Column("completionDate", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["achievementId"],
            ["achievement.id"],
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "achievementId", name="user_achievement_unique"),
    )


def downgrade() -> None:
    op.drop_table("user_achievement")
    op.drop_table("achievement")
