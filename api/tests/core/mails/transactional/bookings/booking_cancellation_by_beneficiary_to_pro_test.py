from dataclasses import asdict
from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.factories as external_bookings_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.categories import subcategories
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    get_booking_cancellation_by_beneficiary_to_pro_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    send_booking_cancellation_by_beneficiary_to_pro_email,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.providers.repository import get_provider_by_local_class


class SendBeneficiaryUserDrivenCancellationEmailToOffererTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_send_booking_cancellation_email_to_offerer(self):
        # Given
        booking = bookings_factories.BookingFactory(
            user__email="user@example.com",
            user__firstName="Guy",
            user__lastName="G.",
            stock__offer__bookingEmail="booking@example.com",
        )

        # When
        send_booking_cancellation_by_beneficiary_to_pro_email(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == "booking@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        )
        assert mails_testing.outbox[0]["reply_to"] == {"email": "user@example.com", "name": "Guy G."}

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.parametrize(
        "venue_factory, event_hour, formatted_price",
        [
            (offerers_factories.VenueFactory, "12h20", "10 €"),
            (offerers_factories.CaledonianVenueFactory, "21h20", "1193 F"),
        ],
    )
    def test_should_send_one_side_booking_cancellation_email(self, venue_factory, event_hour, formatted_price):
        ems_provider = get_provider_by_local_class("EMSStocks")
        stock = offers_factories.EventStockFactory(
            price=10,
            beginningDatetime=datetime(2019, 10, 9, 10, 20, 00),
            offer__bookingEmail="booking@example.com",
            offer__lastProvider=ems_provider,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
            offer__venue=venue_factory(),
        )
        booking = bookings_factories.BookingFactory(
            user__email="user@example.com",
            user__firstName="Guy",
            user__lastName="G.",
            stock=stock,
        )
        external_bookings_factories.ExternalBookingFactory(
            booking=booking,
            barcode="123456789",
            additional_information={
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1257,
                "num_ope": 147149,
            },
        )

        send_booking_cancellation_by_beneficiary_to_pro_email(booking, one_side_cancellation=True)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "booking@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "EVENT_DATE": "mercredi 9 octobre 2019",
            "EVENT_HOUR": event_hour,
            "EXTERNAL_BOOKING_INFORMATION": "barcode: 123456789, additional_information: {'num_ope': 147149, "
            "'num_cine': '9997', 'num_trans': 1257, 'num_caisse': '255'}",
            "IS_EVENT": True,
            "IS_EXTERNAL": True,
            "OFFER_NAME": booking.stock.offer.name,
            "PRICE": booking.stock.price,
            "FORMATTED_PRICE": formatted_price,
            "PROVIDER_NAME": "EMS",
            "QUANTITY": booking.quantity,
            "USER_EMAIL": booking.email,
            "USER_NAME": booking.userName,
            "VENUE_NAME": booking.venue.name,
            "OFFER_ADDRESS": booking.stock.offer.fullAddress,
        }


class MakeOffererBookingRecapEmailAfterUserCancellationTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_sendinblue_data_with_no_ongoing_booking(self):
        # Given
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = bookings_factories.CancelledBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "EVENT_DATE": "mercredi 9 octobre 2019",
            "EVENT_HOUR": "12h20",
            "EXTERNAL_BOOKING_INFORMATION": None,
            "IS_EVENT": True,
            "IS_EXTERNAL": False,
            "OFFER_NAME": stock.offer.name,
            "PRICE": stock.price,
            "FORMATTED_PRICE": "10,10 €",
            "PROVIDER_NAME": None,
            "QUANTITY": booking.quantity,
            "USER_EMAIL": booking.email,
            "USER_NAME": booking.userName,
            "VENUE_NAME": venue.name,
            "OFFER_ADDRESS": booking.stock.offer.fullAddress,
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_return_sendinblue_data_with_ongoing_bookings(self):
        # Given
        stock = offers_factories.EventStockFactory(price=0, beginningDatetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = bookings_factories.CancelledBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        venue = stock.offer.venue
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "EVENT_DATE": "mercredi 9 octobre 2019",
            "EVENT_HOUR": "12h20",
            "EXTERNAL_BOOKING_INFORMATION": None,
            "IS_EVENT": True,
            "IS_EXTERNAL": False,
            "OFFER_NAME": stock.offer.name,
            "PRICE": "Gratuit",
            "FORMATTED_PRICE": "Gratuit",
            "PROVIDER_NAME": None,
            "QUANTITY": booking1.quantity,
            "USER_EMAIL": booking1.email,
            "USER_NAME": booking1.userName,
            "VENUE_NAME": venue.name,
            "OFFER_ADDRESS": booking1.stock.offer.fullAddress,
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_return_numerique_when_venue_is_virtual(self):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        stock = offers_factories.ThingStockFactory(offer__venue=virtual_venue)
        booking1 = bookings_factories.CancelledBookingFactory(stock=stock, quantity=2)

        # When
        email_data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking1)

        # Then
        assert email_data.template == TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        assert email_data.params == {
            "EVENT_DATE": "",
            "EVENT_HOUR": "",
            "EXTERNAL_BOOKING_INFORMATION": None,
            "IS_EVENT": False,
            "IS_EXTERNAL": False,
            "OFFER_NAME": stock.offer.name,
            "PRICE": stock.price,
            "FORMATTED_PRICE": "10,10 €",
            "PROVIDER_NAME": None,
            "QUANTITY": booking1.quantity,
            "USER_EMAIL": booking1.email,
            "USER_NAME": booking1.userName,
            "VENUE_NAME": virtual_venue.name,
            "OFFER_ADDRESS": booking1.stock.offer.fullAddress,
        }
