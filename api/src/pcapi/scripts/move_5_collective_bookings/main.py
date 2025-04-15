"""
Move collective bookings and offers from an offer to a new one after business has been transferred.
Documents have already been checked by support-pro.
"""

import argparse

import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid


OLD_OFFERER_ID = 4925
NEW_OFFERER_ID = 56497
NEW_VENUE_ID = 144958
COLLECTIVE_BOOKING_IDS = [522093, 484440, 435164, 436599, 507823]


def move_collective_offers() -> None:
    collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(
            educational_models.CollectiveBooking.id.in_(COLLECTIVE_BOOKING_IDS),
            educational_models.CollectiveBooking.offererId == OLD_OFFERER_ID,
            educational_models.CollectiveBooking.status.in_(
                [
                    educational_models.CollectiveBookingStatus.CONFIRMED,
                    educational_models.CollectiveBookingStatus.PENDING,
                ]
            ),
        )
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .options(
                sa_orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                    offerers_models.Venue.offererAddress
                ),
                sa_orm.joinedload(educational_models.CollectiveOffer.template)
                .joinedload(educational_models.CollectiveOfferTemplate.venue)
                .joinedload(offerers_models.Venue.offererAddress),
            )
        )
        .all()
    )

    print(f"{len(collective_bookings)}/{len(COLLECTIVE_BOOKING_IDS)} collective bookings found")

    new_venue = db.session.query(offerers_models.Venue).filter_by(id=NEW_VENUE_ID).one()
    print(f"new venue found: {new_venue} {new_venue.common_name}")

    for collective_booking in collective_bookings:
        print(f"collective booking: {collective_booking}")
        collective_booking.offererId = NEW_OFFERER_ID
        collective_booking.venueId = NEW_VENUE_ID

        collective_offer = collective_booking.collectiveStock.collectiveOffer
        print(f"collective offer: {collective_offer} {collective_offer.name}")
        # offers are associated with different venues as addresses, keep the address
        address_id = collective_offer.venue.offererAddress.addressId
        label = collective_offer.venue.common_name
        print(f"address id: {address_id} - label: {label}")
        offerer_address = offerers_api.get_or_create_offerer_address(NEW_OFFERER_ID, address_id, label)
        print(f"new offerer address: {offerer_address}")
        collective_offer.offererAddress = offerer_address
        collective_offer.locationType = educational_models.CollectiveLocationType.ADDRESS
        collective_offer.venueId = NEW_VENUE_ID
        collective_offer.offerVenue["venueId"] = NEW_VENUE_ID

        collective_offer_template = collective_offer.template
        print(f"collective offer template: {collective_offer_template} {collective_offer_template.name}")
        # templates are currently associated with the default venue without offererAddress
        collective_offer_template.offererAddress = None
        collective_offer_template.locationType = None
        collective_offer_template.venueId = NEW_VENUE_ID
        collective_offer_template.offerVenue["venueId"] = NEW_VENUE_ID

        db.session.add(collective_booking)
        db.session.add(collective_offer)
        db.session.add(collective_offer_template)

    db.session.flush()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Move collective offers")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    with atomic():
        move_collective_offers()

        if args.not_dry:
            db.session.commit()
        else:
            mark_transaction_as_invalid()
            print("Dry run finished.")
