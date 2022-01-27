from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    _is_offer_active_for_recap,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    get_booking_cancellation_by_beneficiary_to_pro_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    send_booking_cancellation_by_beneficiary_to_pro_email,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories


class SendBeneficiaryUserDrivenCancellationEmailToOffererTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_send_booking_cancellation_email_to_offerer(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(stock__offer__bookingEmail="booking@example.com")

        # When
        send_booking_cancellation_by_beneficiary_to_pro_email(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking@example.com"
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value.__dict__
        )


class MakeOffererBookingRecapEmailAfterUserCancellationTest:
    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro._is_offer_active_for_recap",
        return_value=True,
    )
    def test_should_return_mailjet_data_with_no_ongoing_booking(
        self, mock_is_offer_active, mock_build_pc_pro_offer_link
    ):
        # Given
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": venue.departementCode,
            "NOM_OFFRE": stock.offer.name,
            "LIEN_OFFRE_PCPRO": "http://pc_pro.com/offer_link",
            "NOM_LIEU": venue.name,
            "PRIX": stock.price,
            "IS_EVENT": True,
            "DATE": "09-Oct-2019",
            "HEURE": "12h20",
            "QUANTITE": booking.quantity,
            "USER_NAME": booking.userName,
            "USER_EMAIL": booking.email,
            "IS_ACTIVE": True,
            "NOMBRE_RESA": 0,
            "USERS": [],
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro._is_offer_active_for_recap",
        return_value=True,
    )
    def test_should_return_mailjet_data_with_ongoing_bookings(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        stock = offers_factories.EventStockFactory(price=0, beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": venue.departementCode,
            "NOM_OFFRE": stock.offer.name,
            "LIEN_OFFRE_PCPRO": "http://pc_pro.com/offer_link",
            "NOM_LIEU": venue.name,
            "PRIX": "Gratuit",
            "IS_EVENT": True,
            "DATE": "09-Oct-2019",
            "HEURE": "12h20",
            "QUANTITE": booking1.quantity,
            "USER_NAME": booking1.userName,
            "USER_EMAIL": booking1.email,
            "IS_ACTIVE": True,
            "NOMBRE_RESA": 1,
            "USERS": [
                {
                    "contremarque": booking2.token,
                    "email": booking2.email,
                    "firstName": booking2.firstName,
                    "lastName": booking2.lastName,
                }
            ],
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro._is_offer_active_for_recap",
        return_value=False,
    )
    def test_should_return_mailjet_data_on_thing_offer(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        stock = offers_factories.ThingStockFactory()
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock, quantity=1)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": venue.departementCode,
            "NOM_OFFRE": stock.offer.name,
            "LIEN_OFFRE_PCPRO": "http://pc_pro.com/offer_link",
            "NOM_LIEU": venue.name,
            "PRIX": stock.price,
            "IS_EVENT": False,
            "DATE": "",
            "HEURE": "",
            "QUANTITE": booking1.quantity,
            "USER_NAME": booking1.userName,
            "USER_EMAIL": booking1.email,
            "IS_ACTIVE": False,
            "NOMBRE_RESA": 1,
            "USERS": [
                {
                    "contremarque": booking2.token,
                    "email": booking2.email,
                    "firstName": booking2.firstName,
                    "lastName": booking2.lastName,
                }
            ],
        }

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro._is_offer_active_for_recap",
        return_value=False,
    )
    def test_should_return_numerique_when_venue_is_virtual(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        virtual_venue = offers_factories.VirtualVenueFactory()
        stock = offers_factories.ThingStockFactory(offer__venue=virtual_venue)
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)
        booking2 = bookings_factories.IndividualBookingFactory(stock=stock)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": "numérique",
            "NOM_OFFRE": stock.offer.name,
            "LIEN_OFFRE_PCPRO": "http://pc_pro.com/offer_link",
            "NOM_LIEU": virtual_venue.name,
            "PRIX": stock.price,
            "IS_EVENT": False,
            "DATE": "",
            "HEURE": "",
            "QUANTITE": booking1.quantity,
            "USER_NAME": booking1.userName,
            "USER_EMAIL": booking1.email,
            "IS_ACTIVE": False,
            "NOMBRE_RESA": 1,
            "USERS": [
                {
                    "contremarque": booking2.token,
                    "email": booking2.email,
                    "firstName": booking2.firstName,
                    "lastName": booking2.lastName,
                }
            ],
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
