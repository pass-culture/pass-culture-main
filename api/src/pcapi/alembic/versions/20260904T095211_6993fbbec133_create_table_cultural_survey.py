"""Create user_cultural_survey table"""

import sqlalchemy as sa
from alembic import op


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
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("createdAt", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_foreign_key(
        "user_cultural_survey_fkey",
        "user_cultural_survey",
        "user",
        ["userId"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_table("user_cultural_survey")
