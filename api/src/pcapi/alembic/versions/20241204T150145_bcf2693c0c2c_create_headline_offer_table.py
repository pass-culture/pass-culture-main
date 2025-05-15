"""
Create headline offer table
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bcf2693c0c2c"
down_revision = "58f3ca2882c6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "headline_offer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("dateUpdated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_headline_offer_offerId"), "headline_offer", ["offerId"], unique=True)
    op.create_index(op.f("ix_headline_offer_venueId"), "headline_offer", ["venueId"], unique=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_headline_offer_venueId"),
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_headline_offer_offerId"),
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_table(
            "headline_offer",
            if_exists=True,
        )
