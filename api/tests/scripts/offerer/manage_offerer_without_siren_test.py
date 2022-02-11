import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.scripts.offerer.manage_offerer_without_siren import manage_offerer_without_siren


@pytest.mark.usefixtures("db_session")
def test_manage_offerer_without_siren():
    # Given
    offerer_without_venue = OffererFactory(siren=None)

    offerer_without_offer = OffererFactory(siren=None)
    VenueFactory(managingOfferer=offerer_without_offer)

    offerer_with_all_bookings_reimbursed = OffererFactory(siren=None)
    venue_with_all_bookings_reimbursed = VenueFactory(managingOfferer=offerer_with_all_bookings_reimbursed)
    BookingFactory(
        stock__offer__venue=venue_with_all_bookings_reimbursed,
        offerer=offerer_with_all_bookings_reimbursed,
        status=BookingStatus.REIMBURSED,
    )
    BookingFactory(
        stock__offer__venue=venue_with_all_bookings_reimbursed,
        offerer=offerer_with_all_bookings_reimbursed,
        status=BookingStatus.CANCELLED,
    )

    offerer_with_booking_not_reimbursed = OffererFactory(siren=None)
    venue_with_booking_not_reimbursed = VenueFactory(managingOfferer=offerer_with_booking_not_reimbursed)
    BookingFactory(
        stock__offer__venue=venue_with_booking_not_reimbursed,
        status=BookingStatus.USED,
    )

    # When
    ids = [
        offerer_without_venue.id,
        offerer_without_offer.id,
        offerer_with_all_bookings_reimbursed.id,
        offerer_with_booking_not_reimbursed.id,
    ]
    manage_offerer_without_siren(ids)

    # Then
    assert offerer_without_venue.isActive == False
    assert offerer_without_offer.isActive == False
    # # one venue was deleted
    assert Venue.query.count() == 2
    assert offerer_with_all_bookings_reimbursed.isActive == False
    assert offerer_with_booking_not_reimbursed.isActive == True
