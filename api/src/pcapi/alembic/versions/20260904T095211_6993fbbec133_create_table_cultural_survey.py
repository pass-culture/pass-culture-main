"""Create user_cultural_survey table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6993fbbec133"
down_revision = "a703309b6657"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_cultural_survey",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("answers", postgresql.JSONB, nullable=False),
        sa.Column("createdAt", sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", name=op.f("user_cultural_survey_userId_unique")),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], name=op.f("user_cultural_survey_userId_fkey")),
    )


def downgrade() -> None:
    op.drop_table("user_cultural_survey")
