from dataclasses import asdict
from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
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
        booking = bookings_factories.IndividualBookingFactory(
            individualBooking__user__email="user@example.com",
            individualBooking__user__firstName="Guy",
            individualBooking__user__lastName="G.",
            stock__offer__bookingEmail="booking@example.com",
        )

        # When
        send_booking_cancellation_by_beneficiary_to_pro_email(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking@example.com"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["reply_to"] == {"email": "user@example.com", "name": "Guy G."}


class MakeOffererBookingRecapEmailAfterUserCancellationTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_mailjet_data_with_no_ongoing_booking(self):
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
            "NOM_LIEU": venue.name,
            "PRIX": stock.price,
            "IS_EVENT": True,
            "DATE": "09-Oct-2019",
            "HEURE": "12h20",
            "QUANTITE": booking.quantity,
            "USER_NAME": booking.userName,
            "USER_EMAIL": booking.email,
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_return_mailjet_data_with_ongoing_bookings(self):
        # Given
        stock = offers_factories.EventStockFactory(price=0, beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": venue.departementCode,
            "NOM_OFFRE": stock.offer.name,
            "NOM_LIEU": venue.name,
            "PRIX": "Gratuit",
            "IS_EVENT": True,
            "DATE": "09-Oct-2019",
            "HEURE": "12h20",
            "QUANTITE": booking1.quantity,
            "USER_NAME": booking1.userName,
            "USER_EMAIL": booking1.email,
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_return_numerique_when_venue_is_virtual(self):
        # Given
        virtual_venue = offers_factories.VirtualVenueFactory()
        stock = offers_factories.ThingStockFactory(offer__venue=virtual_venue)
        booking1 = bookings_factories.CancelledIndividualBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "DEPARTEMENT": "numérique",
            "NOM_OFFRE": stock.offer.name,
            "NOM_LIEU": virtual_venue.name,
            "PRIX": stock.price,
            "IS_EVENT": False,
            "DATE": "",
            "HEURE": "",
            "QUANTITE": booking1.quantity,
            "USER_NAME": booking1.userName,
            "USER_EMAIL": booking1.email,
        }
