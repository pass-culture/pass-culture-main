"""Add HighlightRequest table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dd84f6234bdb"
down_revision = "a0acdfe3cfc5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "highlight_request",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("highlightId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["highlightId"],
            ["highlight.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("highlightId", "offerId", name="unique_highlight_request_per_offer"),
    )


def downgrade() -> None:
    op.drop_table("highlight_request", if_exists=True)
