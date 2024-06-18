"""Add future_offer table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a07d08bb52cf"
down_revision = "f830372aa947"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "future_offer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("publicationDate", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_future_offer_offerId"),
            "future_offer",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_future_offer_publicationDate"),
            "future_offer",
            ["publicationDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    op.drop_table("future_offer")
