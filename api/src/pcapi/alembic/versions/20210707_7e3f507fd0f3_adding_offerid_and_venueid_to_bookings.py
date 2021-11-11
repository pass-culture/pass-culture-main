"""Adding offerId and venueId to bookings

Revision ID: 7e3f507fd0f3
Revises: 02c37d39e46c
Create Date: 2021-07-07 09:52:27.288673

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "7e3f507fd0f3"
down_revision = "02c37d39e46c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking", sa.Column("offererId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_booking_offererId"), "booking", ["offererId"], unique=False)
    op.create_foreign_key(None, "booking", "offerer", ["offererId"], ["id"])

    op.add_column("booking", sa.Column("venueId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_booking_venueId"), "booking", ["venueId"], unique=False)
    op.create_foreign_key(None, "booking", "venue", ["venueId"], ["id"])

    if not settings.IS_STAGING and not settings.IS_PROD:
        op.execute(
            text(
                """
             WITH "bookingByOfferer" AS
            (SELECT b.id, venue."managingOffererId", venue.id "venueId"
                FROM booking b JOIN stock ON stock.id = b."stockId"
                JOIN offer ON offer.id = stock."offerId"
                JOIN venue on offer."venueId" = venue.id
                WHERE b."venueId" is null)
            UPDATE booking SET "offererId"=bbo."managingOffererId", "venueId"=bbo."venueId" FROM "bookingByOfferer" bbo
            WHERE booking.id=bbo.id
            """
            )
        )


def downgrade() -> None:
    op.drop_column("booking", "offererId")
    op.drop_column("booking", "venueId")
