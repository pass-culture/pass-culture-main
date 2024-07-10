from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


@pytest.mark.usefixtures("db_session")
class FormatDateAndHourForEmailTest:
    def test_should_return_formatted_event_beginningDatetime_when_offer_is_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_date_for_email(booking) == "09-Oct-2019"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        assert format_booking_date_for_email(booking) == ""


@pytest.mark.usefixtures("db_session")
class FormatBookingHoursForEmailTest:
    def test_should_return_hours_and_minutes_from_beginningDatetime_when_contains_hours(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_hours_for_email(booking) == "12h20"

    def test_should_return_only_hours_from_event_beginningDatetime_when_oclock(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 13),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_hours_for_email(booking) == "15h"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        assert format_booking_hours_for_email(booking) == ""

    @override_features(WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE=True)
    def test_should_return_hours_and_minutes_casted_in_the_venue_timezone(self):
        # When offer has no offererAddress but venue has, use the venue's offererAddress TZ
        offerer = offerers_factories.OffererFactory()
        offerer_address = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
            address__departmentCode="972",  # Amerique/Martinique
        )
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            stock__offer__venue__managingOfferer=offerer,
            stock__offer__venue__offererAddress=offerer_address,
            stock__offer__offererAddress=None,
        )
        assert not booking.stock.offer.offererAddressId
        assert format_booking_hours_for_email(booking) == "6h20"

    @override_features(WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE=True)
    def test_should_return_hours_and_minutes_casted_in_the_offer_timezone(self):
        # When offer and venue have offererAddress use the offer's offererAddress TZ
        offerer = offerers_factories.OffererFactory()
        venue_offerer_address = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
            address__departmentCode="75",  # Europe/Paris
        )
        offer_offerer_address = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="9 Boulevard de Bercy",
            address__banId="75112_0877_00009",
            address__departmentCode="972",  # Amerique/Martinique
        )
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            stock__offer__venue__managingOfferer=offerer,
            stock__offer__venue__offererAddress=venue_offerer_address,
            stock__offer__offererAddress=offer_offerer_address,
        )
        assert booking.stock.offer.offererAddressId != booking.stock.offer.venue.offererAddressId
        assert format_booking_hours_for_email(booking) == "6h20"
