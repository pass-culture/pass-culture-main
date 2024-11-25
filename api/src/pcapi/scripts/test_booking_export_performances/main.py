import argparse
from datetime import date
from datetime import datetime
from datetime import timedelta
import typing
from unittest.mock import patch

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.orm import aliased

from pcapi.app import app
from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization.bookings_recap_serialize import BookingStatusFilter


app.app_context().push()


##########
# code to benchmark


def _get_filtered_bookings_query(
    pro_user: User,
    *,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    extra_joins: tuple[tuple[typing.Any, ...], ...] = (),
) -> BaseQuery:
    VenueOffererAddress = aliased(OffererAddress)
    VenueAddress = aliased(Address)
    bookings_query = (
        Booking.query.join(Booking.offerer)
        .join(Offerer.UserOfferers)
        .join(Booking.stock)
        .join(Stock.offer)
        .join(Booking.externalBookings, isouter=True)
        .join(Booking.venue, isouter=True)
    )
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        bookings_query = (
            bookings_query.outerjoin(Offer.offererAddress)
            .outerjoin(OffererAddress.address)
            .outerjoin(VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id)
            .outerjoin(VenueAddress, VenueOffererAddress.addressId == VenueAddress.id)
        )
    for join_key, *join_conditions in extra_joins:
        if join_conditions:
            bookings_query = bookings_query.join(join_key, *join_conditions, isouter=True)
        else:
            bookings_query = bookings_query.join(join_key, isouter=True)
    if not pro_user.has_admin_role:
        bookings_query = bookings_query.filter(UserOfferer.user == pro_user)
    bookings_query = bookings_query.filter(UserOfferer.isValidated)
    if period:
        period_attribut_filter = (
            booking_repository.BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else booking_repository.BOOKING_DATE_STATUS_MAPPING[BookingStatusFilter.BOOKED]
        )
        # Cheat code enabled: extends the period by 1 day on each side.
        # We'll filter with timezones afterward but allows postgresql to use indexes
        if period[0] > period[1]:
            period = (period[1] - timedelta(days=1), period[0] + timedelta(days=1))
        else:
            period = (period[0] - timedelta(days=1), period[1] + timedelta(days=1))
        bookings_query = bookings_query.filter(period_attribut_filter.between(*period, symmetric=True))
    if venue_id is not None:
        bookings_query = bookings_query.filter(Booking.venueId == venue_id)
    if offer_id is not None:
        bookings_query = bookings_query.filter(Stock.offerId == offer_id)
    if offerer_address_id:
        bookings_query = bookings_query.filter(Offer.offererAddressId == offerer_address_id)
    if event_date:
        # Same as above, let's take 1 day on both side and filter afterward
        bookings_query = bookings_query.filter(
            Stock.beginningDatetime.between(event_date - timedelta(days=1), event_date + timedelta(days=1))
        )
    return bookings_query


##########


def benchmark_bookings(dry_run: bool) -> None:
    # We know this user and those parameters have a timeout issue
    user = User.query.get(1321)
    # page = 1
    # per_page_limit = 1000
    venue_id = None
    # offer_id = None
    # offerer_address_id = None
    event_date = None
    booking_status = BookingStatusFilter.BOOKED
    booking_period = (date(2024, 10, 28), date(2024, 11, 3))

    # New query duration
    with patch("pcapi.core.bookings.repository._get_filtered_bookings_query", _get_filtered_bookings_query):
        start = datetime.utcnow()
        booking_repository._get_filtered_booking_report(
            pro_user=user, period=booking_period, status_filter=booking_status, event_date=event_date, venue_id=venue_id
        ).all()
        print("New query duration: %s" % (datetime.utcnow() - start))

    # New query duration
    with patch("pcapi.core.bookings.repository._get_filtered_bookings_query", _get_filtered_bookings_query):
        start = datetime.utcnow()
        booking_repository.get_export(
            user, booking_period=booking_period, status_filter=booking_status, event_date=event_date, venue_id=venue_id
        )
        print("New export duration: %s" % (datetime.utcnow() - start))

    # Original query duration
    start = datetime.utcnow()
    booking_repository._get_filtered_booking_report(
        pro_user=user, period=booking_period, status_filter=booking_status, event_date=event_date, venue_id=venue_id
    ).all()
    print("Original query duration: %s" % (datetime.utcnow() - start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        db.session.execute(sa.text("set session statement_timeout = '900s'"))
        benchmark_bookings(args.dry_run)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
    else:
        db.session.commit()
