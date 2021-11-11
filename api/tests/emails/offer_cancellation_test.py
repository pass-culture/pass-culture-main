from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.emails.beneficiary_offer_cancellation import (
    retrieve_offerer_booking_recap_email_data_after_user_cancellation,
)
from pcapi.emails.beneficiary_offer_cancellation import _is_offer_active_for_recap
from pcapi.utils.mailing import make_offerer_driven_cancellation_email_for_offerer


class MakeOffererDrivenCancellationEmailForOffererTest:
    @pytest.mark.usefixtures("db_session")
    def test_make_offerer_driven_cancellation_email_for_offerer_event_when_no_other_booking(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        stock = offers_factories.EventStockFactory(
            beginningDatetime=beginning_datetime, price=20, quantity=10, bookingLimitDatetime=booking_limit_datetime
        )
        booking = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        with patch("pcapi.utils.mailing.find_ongoing_bookings_by_stock", return_value=[]):
            email = make_offerer_driven_cancellation_email_for_offerer(booking)

        # Then
        venue = stock.offer.venue
        email_html = BeautifulSoup(email["Html-part"], "html.parser")
        html_action = str(email_html.find("p", {"id": "action"}))
        html_recap = str(email_html.find("p", {"id": "recap"}))
        html_no_recal = str(email_html.find("p", {"id": "no-recap"}))
        assert "Vous venez d'annuler" in html_action
        assert booking.publicName in html_action
        assert booking.email in html_action
        assert f"pour {stock.offer.name}" in html_recap
        assert f"proposé par {venue.name}" in html_recap
        assert "le 20 juillet 2019 à 14:00" in html_recap
        assert venue.address in html_recap
        assert venue.city in html_recap
        assert venue.postalCode in html_recap
        assert "Aucune réservation" in html_no_recal
        assert (
            email["Subject"]
            == f"Confirmation de votre annulation de réservation pour {stock.offer.name}, proposé par {venue.name}"
        )

    @pytest.mark.usefixtures("db_session")
    def test_make_offerer_driven_cancellation_email_for_offerer_event_when_other_booking(self, app):
        # Given
        other_beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc), price=20, quantity=10
        )
        booking1 = bookings_factories.IndividualBookingFactory(stock=stock, token="98765")
        booking2 = bookings_factories.IndividualBookingFactory(
            individualBooking__user=other_beneficiary, stock=stock, token="12345"
        )

        # When
        with patch("pcapi.utils.mailing.find_ongoing_bookings_by_stock", return_value=[booking2]):
            email = make_offerer_driven_cancellation_email_for_offerer(booking1)

        # Then
        email_html = BeautifulSoup(email["Html-part"], "html.parser")
        html_recap_table = email_html.find("table", {"id": "recap-table"}).text
        assert "Prénom" in html_recap_table
        assert "Nom" in html_recap_table
        assert "Email" in html_recap_table
        assert other_beneficiary.firstName in html_recap_table
        assert other_beneficiary.lastName in html_recap_table
        assert other_beneficiary.email in html_recap_table
        assert booking2.token in html_recap_table

    @pytest.mark.usefixtures("db_session")
    def test_make_offerer_driven_cancellation_email_for_offerer_thing_and_already_existing_booking(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(price=0, quantity=10)
        booking = bookings_factories.IndividualBookingFactory(stock=stock, token="12346")

        booking2 = bookings_factories.IndividualBookingFactory(stock=stock, token="12345")
        ongoing_bookings = [booking2]

        # When
        with patch("pcapi.utils.mailing.find_ongoing_bookings_by_stock", return_value=ongoing_bookings):
            email = make_offerer_driven_cancellation_email_for_offerer(booking)

        # Then
        venue = stock.offer.venue
        email_html = BeautifulSoup(email["Html-part"], "html.parser")
        html_action = str(email_html.find("p", {"id": "action"}))
        html_recap = email_html.find("p", {"id": "recap"}).text
        html_recap_table = email_html.find("table", {"id": "recap-table"}).text
        assert "Vous venez d'annuler" in html_action
        assert booking.publicName in html_action
        assert booking.email in html_action
        assert f"pour {stock.offer.product.name}" in html_recap
        assert f"proposé par {venue.name}" in html_recap
        assert venue.address in html_recap
        assert venue.city in html_recap
        assert venue.postalCode in html_recap
        assert booking2.firstName in html_recap_table
        assert booking2.email in html_recap_table
        assert booking.token not in html_recap_table
        assert booking2.token not in html_recap_table
        assert (
            email["Subject"]
            == f"Confirmation de votre annulation de réservation pour {stock.offer.product.name}, proposé par {venue.name}"
        )


class MakeOffererBookingRecapEmailAfterUserCancellationWithMailjetTemplateTest:
    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.emails.beneficiary_offer_cancellation.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch("pcapi.emails.beneficiary_offer_cancellation._is_offer_active_for_recap", return_value=True)
    def test_should_return_mailjet_data_with_no_ongoing_booking(
        self, mock_is_offer_active, mock_build_pc_pro_offer_link
    ):
        # Given
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking)

        # Then
        venue = stock.offer.venue
        assert mailjet_data == {
            "MJ-TemplateID": 780015,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "departement": venue.departementCode,
                "nom_offre": stock.offer.name,
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "nom_lieu": venue.name,
                "prix": f"{stock.price}",
                "is_event": 1,
                "date": "09-Oct-2019",
                "heure": "12h20",
                "quantite": booking.quantity,
                "user_name": booking.publicName,
                "user_email": booking.email,
                "is_active": 1,
                "nombre_resa": 0,
                "users": [],
            },
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.emails.beneficiary_offer_cancellation.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch("pcapi.emails.beneficiary_offer_cancellation._is_offer_active_for_recap", return_value=True)
    def test_should_return_mailjet_data_with_ongoing_bookings(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        stock = offers_factories.EventStockFactory(price=0, beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1)

        # Then
        venue = stock.offer.venue
        assert mailjet_data == {
            "MJ-TemplateID": 780015,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "departement": venue.departementCode,
                "nom_offre": stock.offer.name,
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "nom_lieu": venue.name,
                "prix": "Gratuit",
                "is_event": 1,
                "date": "09-Oct-2019",
                "heure": "12h20",
                "quantite": booking1.quantity,
                "user_name": booking1.publicName,
                "user_email": booking1.email,
                "is_active": 1,
                "nombre_resa": 1,
                "users": [
                    {
                        "contremarque": booking2.token,
                        "email": booking2.email,
                        "firstName": booking2.firstName,
                        "lastName": booking2.lastName,
                    }
                ],
            },
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.emails.beneficiary_offer_cancellation.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch("pcapi.emails.beneficiary_offer_cancellation._is_offer_active_for_recap", return_value=False)
    def test_should_return_mailjet_data_on_thing_offer(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        stock = offers_factories.ThingStockFactory()
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock, quantity=1)

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1)

        # Then
        venue = stock.offer.venue
        assert mailjet_data == {
            "MJ-TemplateID": 780015,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "departement": venue.departementCode,
                "nom_offre": stock.offer.name,
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "nom_lieu": venue.name,
                "prix": f"{stock.price}",
                "is_event": 0,
                "date": "",
                "heure": "",
                "quantite": booking1.quantity,
                "user_name": booking1.publicName,
                "user_email": booking1.email,
                "is_active": 0,
                "nombre_resa": 1,
                "users": [
                    {
                        "contremarque": booking2.token,
                        "email": booking2.email,
                        "firstName": booking2.firstName,
                        "lastName": booking2.lastName,
                    }
                ],
            },
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.emails.beneficiary_offer_cancellation.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch("pcapi.emails.beneficiary_offer_cancellation._is_offer_active_for_recap", return_value=False)
    def test_should_return_numerique_when_venue_is_virtual(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        virtual_venue = offers_factories.VirtualVenueFactory()
        stock = offers_factories.ThingStockFactory(offer__venue=virtual_venue)
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 780015,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "departement": "numérique",
                "nom_offre": stock.offer.name,
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "nom_lieu": virtual_venue.name,
                "prix": f"{stock.price}",
                "is_event": 0,
                "date": "",
                "heure": "",
                "quantite": booking1.quantity,
                "user_name": booking1.publicName,
                "user_email": booking1.email,
                "is_active": 0,
                "nombre_resa": 1,
                "users": [
                    {
                        "contremarque": booking2.token,
                        "email": booking2.email,
                        "firstName": booking2.firstName,
                        "lastName": booking2.lastName,
                    }
                ],
            },
        }


class IsOfferActiveForRecapTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_offer_is_active_and_stock_still_bookable(self, app):
        # Given
        event_date = datetime.now() + timedelta(days=6)
        stock = offers_factories.EventStockFactory(
            offer__isActive=True, quantity=2, bookingLimitDatetime=event_date, beginningDatetime=event_date
        )

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert is_active

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offer_is_not_active(self, app):
        # Given
        event_date = datetime.now() + timedelta(days=6)
        stock = offers_factories.EventStockFactory(
            offer__isActive=False, quantity=2, bookingLimitDatetime=event_date, beginningDatetime=event_date
        )

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_stock_has_no_remaining_quantity(self, app):
        # Given
        event_date = datetime.now() + timedelta(days=6)
        stock = offers_factories.EventStockFactory(
            offer__isActive=True, price=0, quantity=2, bookingLimitDatetime=event_date, beginningDatetime=event_date
        )
        bookings_factories.IndividualBookingFactory(stock=stock, quantity=2)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_stock_booking_limit_is_past(self, app):
        # Given
        stock = offers_factories.EventStockFactory(
            offer__isActive=True, price=0, quantity=2, bookingLimitDatetime=datetime.now() - timedelta(days=6)
        )
        bookings_factories.IndividualBookingFactory(stock=stock, quantity=2)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stock_is_unlimited(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(offer__isActive=True, price=0, quantity=None)
        bookings_factories.IndividualBookingFactory(stock=stock, quantity=2)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert is_active

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_stock_is_unlimited_but_booking_date_is_past(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(
            offer__isActive=True, price=0, quantity=None, bookingLimitDatetime=datetime.now() - timedelta(days=6)
        )
        bookings_factories.IndividualBookingFactory(stock=stock, quantity=2)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active
