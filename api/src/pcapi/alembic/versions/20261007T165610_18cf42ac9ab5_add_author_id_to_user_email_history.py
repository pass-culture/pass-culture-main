"""Add authorId (user) FK column to user_email_history"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "18cf42ac9ab5"
down_revision = "7b723528671a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_email_history",
        sa.Column("authorId", sa.BigInteger(), nullable=True),
        if_not_exists=True,
    )
    op.create_foreign_key(
        "user_email_history_authorId_fkey",
        "user_email_history",
        "user",
        ["authorId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "user_email_history_authorId_fkey",
        "user_email_history",
        type_="foreignkey",
        if_exists=True,
    )
    op.drop_column("user_email_history", "authorId", if_exists=True)
