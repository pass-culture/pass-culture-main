from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_settings
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


@override_settings(PRO_URL="http://pcpro.com")
def test_build_pc_pro_offer_link():
    offer = offers_factories.OfferFactory.build(id=123)
    human_id = humanize(offer.id)

    url = build_pc_pro_offer_link(offer)

    assert url == f"http://pcpro.com/offre/{human_id}/individuel/edition"


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
