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
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_highlight_request_highlightId"),
            "highlight_request",
            ["highlightId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_highlight_request_offerId"),
            "highlight_request",
            ["offerId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_highlight_request_highlightId"),
            table_name="highlight_request",
            postgresql_concurrently=True,
            if_exists=True,
        )
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_highlight_request_offerId"),
            table_name="highlight_request",
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_table("highlight_request", if_exists=True)
