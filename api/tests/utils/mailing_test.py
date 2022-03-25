from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


class BuildPcProOfferLinkTest:
    @patch("pcapi.settings.PRO_URL", "http://pcpro.com")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_pc_pro_offer_link(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        repository.save(offer)
        offer_id = humanize(offer.id)

        # When
        pc_pro_url = build_pc_pro_offer_link(offer)

        # Then
        assert pc_pro_url == f"http://pcpro.com/offre/{offer_id}/individuel/edition"


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
