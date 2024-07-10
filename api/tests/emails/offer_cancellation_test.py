from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.mails.transactional.bookings.booking_cancellation import (
    get_booking_cancellation_confirmation_by_pro_email_data,
)
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories


class MakeOffererDrivenCancellationEmailForOffererTest:
    @override_features(WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE=True)
    @pytest.mark.usefixtures("db_session")
    def test_offer_cancellation_confirmation_by_offerer_event_when_no_other_booking(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        offerer_address = offerers_factories.OffererAddressFactory(
            address__departmentCode="972",  # Amerique/Martinique
        )
        stock = offers_factories.EventStockFactory(
            beginningDatetime=beginning_datetime,
            price=20,
            quantity=10,
            bookingLimitDatetime=booking_limit_datetime,
            offer__offererAddress=None,
            offer__venue__offererAddress=offerer_address,
            offer__venue__managingOfferer=offerer_address.offerer,
        )
        booking = bookings_factories.BookingFactory(stock=stock)

        # When
        with patch("pcapi.core.bookings.repository.find_ongoing_bookings_by_stock", return_value=[]):
            email = get_booking_cancellation_confirmation_by_pro_email_data(booking)

        # Then
        venue = stock.offer.venue
        email_html = BeautifulSoup(email.html_content, "html.parser")
        html_action = str(email_html.find("p", {"id": "action"}))
        html_recap = str(email_html.find("p", {"id": "recap"}))
        assert "Vous venez d'annuler" in html_action
        assert booking.userName in html_action
        assert booking.email in html_action
        assert f"pour {stock.offer.name}" in html_recap
        assert f"proposé par {venue.name}" in html_recap
        assert "le 20 juillet 2019, 08:00" in html_recap
        assert venue.street in html_recap
        assert venue.city in html_recap
        assert venue.postalCode in html_recap

        assert (
            email.subject
            == f"Confirmation de votre annulation de réservation pour {stock.offer.name}, proposé par {venue.name}"
        )
        html_no_recap = str(email_html.find("p", {"id": "no-recap"}))
        assert "Aucune réservation" in html_no_recap

    @pytest.mark.usefixtures("db_session")
    def test_offer_cancellation_confirmation_by_offerer_event_when_no_other_booking_without_offerer_address(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        stock = offers_factories.EventStockFactory(
            beginningDatetime=beginning_datetime, price=20, quantity=10, bookingLimitDatetime=booking_limit_datetime
        )
        booking = bookings_factories.BookingFactory(stock=stock)

        # When
        with patch("pcapi.core.bookings.repository.find_ongoing_bookings_by_stock", return_value=[]):
            email = get_booking_cancellation_confirmation_by_pro_email_data(booking)

        # Then
        venue = stock.offer.venue
        email_html = BeautifulSoup(email.html_content, "html.parser")
        html_action = str(email_html.find("p", {"id": "action"}))
        html_recap = str(email_html.find("p", {"id": "recap"}))
        assert "Vous venez d'annuler" in html_action
        assert booking.userName in html_action
        assert booking.email in html_action
        assert f"pour {stock.offer.name}" in html_recap
        assert f"proposé par {venue.name}" in html_recap
        assert "le 20 juillet 2019, 14:00" in html_recap
        assert venue.street in html_recap
        assert venue.city in html_recap
        assert venue.postalCode in html_recap

        assert (
            email.subject
            == f"Confirmation de votre annulation de réservation pour {stock.offer.name}, proposé par {venue.name}"
        )
        html_no_recap = str(email_html.find("p", {"id": "no-recap"}))
        assert "Aucune réservation" in html_no_recap

    @pytest.mark.usefixtures("db_session")
    def test_offer_cancellation_confirmation_by_offerer_event_when_other_booking(self, app):
        # Given
        other_beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc), price=20, quantity=10
        )
        booking1 = bookings_factories.BookingFactory(stock=stock, token="98765")
        booking2 = bookings_factories.BookingFactory(user=other_beneficiary, stock=stock, token="12345")

        # When
        with patch("pcapi.core.bookings.repository.find_ongoing_bookings_by_stock", return_value=[booking2]):
            email = get_booking_cancellation_confirmation_by_pro_email_data(booking1)

        # Then
        email_html = BeautifulSoup(email.html_content, "html.parser")
        html_recap_table = email_html.find("table", {"id": "recap-table"}).text
        assert "Prénom" in html_recap_table
        assert "Nom" in html_recap_table
        assert "Email" in html_recap_table
        assert other_beneficiary.firstName in html_recap_table
        assert other_beneficiary.lastName in html_recap_table
        assert other_beneficiary.email in html_recap_table
        assert booking2.token in html_recap_table

    @pytest.mark.usefixtures("db_session")
    def test_offer_cancellation_confirmation_by_offerer_thing_and_already_existing_booking(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(price=0, quantity=10)
        booking = bookings_factories.BookingFactory(stock=stock, token="12346")

        booking2 = bookings_factories.BookingFactory(stock=stock, token="12345")
        ongoing_bookings = [booking2]

        # When
        with patch("pcapi.core.bookings.repository.find_ongoing_bookings_by_stock", return_value=ongoing_bookings):
            email = get_booking_cancellation_confirmation_by_pro_email_data(booking)

        # Then
        venue = stock.offer.venue
        email_html = BeautifulSoup(email.html_content, "html.parser")
        html_action = str(email_html.find("p", {"id": "action"}))
        html_recap = email_html.find("p", {"id": "recap"}).text
        html_recap_table = email_html.find("table", {"id": "recap-table"}).text
        assert "Vous venez d'annuler" in html_action
        assert booking.userName in html_action
        assert booking.email in html_action
        assert f"pour {stock.offer.name}" in html_recap
        assert f"proposé par {venue.name}" in html_recap
        assert venue.street in html_recap
        assert venue.city in html_recap
        assert venue.postalCode in html_recap
        assert booking2.firstName in html_recap_table
        assert booking2.email in html_recap_table
        assert booking.token not in html_recap_table
        assert booking2.token not in html_recap_table
        assert (
            email.subject
            == f"Confirmation de votre annulation de réservation pour {stock.offer.name}, proposé par {venue.name}"
        )
