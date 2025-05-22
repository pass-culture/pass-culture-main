"""
create table gdpr_user_data_extract
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "048bdcee32e9"
down_revision = "b423e5c9abca"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gdpr_user_data_extract",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("dateProcessed", sa.DateTime(), nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("authorUserId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["authorUserId"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("gdpr_user_data_extract")
