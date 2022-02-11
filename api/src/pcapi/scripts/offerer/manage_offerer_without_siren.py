import logging
from typing import Iterable

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


logger = logging.getLogger(__name__)


def manage_offerer_without_siren(offerer_ids: Iterable[int]) -> None:
    soft_deleted_offerer = []
    offerers_with_booking_not_reimbursed = []
    not_existing_offerers = []
    for offerer_id in offerer_ids:
        should_offerer_be_soft_deleted = True
        try:
            offerer = Offerer.query.filter(Offerer.id == offerer_id).one()
        except NoResultFound:
            not_existing_offerers.append(offerer_id)
        venues = Venue.query.filter(Venue.managingOffererId == offerer.id).all()
        for venue in venues:
            venue_has_not_reimbursed_bookings = db.session.query(
                Booking.query.filter(
                    Booking.venueId == venue.id,
                    and_(Booking.status != BookingStatus.REIMBURSED, Booking.status != BookingStatus.CANCELLED),
                ).exists()
            ).scalar()
            if venue_has_not_reimbursed_bookings:
                should_offerer_be_soft_deleted = False
            else:
                try:
                    delete_cascade_venue_by_id(venue.id)
                except CannotDeleteVenueWithBookingsException:
                    logging.info(
                        "Cannot delete venue with booking",
                        extra={
                            "OffererId": offerer_id,
                            "VenueId": venue.id,
                        },
                    )
        if should_offerer_be_soft_deleted:
            soft_deleted_offerer.append(offerer_id)
            offerer.isActive = False
        else:
            offerers_with_booking_not_reimbursed.append(offerer_id)
    db.session.commit()
    recap_data = {
        "soft_deleted_offerer": soft_deleted_offerer,
        "offerers_with_booking_not_reimbursed": offerers_with_booking_not_reimbursed,
        "not_existing_offerers": not_existing_offerers,
    }
    logging.info("Manage offerers without siren", extra=recap_data)
