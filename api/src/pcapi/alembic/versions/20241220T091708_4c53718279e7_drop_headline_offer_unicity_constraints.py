"""
Drop headline offer unicity constraints on offer and venue
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4c53718279e7"
down_revision = "b18478ab2ea8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_headline_offer_offerId",
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            op.f("ix_headline_offer_offerId"),
            "headline_offer",
            ["offerId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.drop_index(
            "ix_headline_offer_venueId",
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            op.f("ix_headline_offer_venueId"),
            "headline_offer",
            ["venueId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_headline_offer_venueId"),
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            "ix_headline_offer_venueId",
            "headline_offer",
            ["venueId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.drop_index(
            op.f("ix_headline_offer_offerId"),
            table_name="headline_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            "ix_headline_offer_offerId",
            "headline_offer",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
