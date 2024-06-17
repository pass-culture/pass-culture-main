import dataclasses
import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    get_booking_event_reminder_to_beneficiary_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    send_individual_booking_event_reminder_email_to_beneficiary,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class SendEventReminderEmailToBeneficiaryTest:
    def test_sendinblue_send_email(self):
        booking = BookingFactory(stock=offers_factories.EventStockFactory())

        send_individual_booking_event_reminder_email_to_beneficiary(booking)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY.value
        )

    @override_features(WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY=True)
    def should_use_template_with_metadata_when_FF_is_enabled(self):
        booking = BookingFactory(stock=offers_factories.EventStockFactory())

        send_individual_booking_event_reminder_email_to_beneficiary(booking)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY_WITH_METADATA.value
        )

    def should_not_try_to_send_email_when_there_is_no_data(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=None,
                bookingLimitDatetime=None,
            ),
        )

        send_individual_booking_event_reminder_email_to_beneficiary(booking)

        assert len(mails_testing.outbox) == 0


class GetBookingEventReminderToBeneficiaryEmailDataTest:
    def test_given_nominal_booking_event(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__name="Le Petit Rintintin",
                offer__name="Product",
                beginningDatetime=datetime.datetime(2032, 1, 1, 10, 30),
                offer__offererAddress=None,
            ),
            token="N2XPV5",
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params == {
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
            "EVENT_DATETIME_ISO": "2032-01-01T11:30:00+01:00",
            "EVENT_DATE": "1 janvier 2032",
            "EVENT_HOUR": "11h30",
            "IS_DUO_EVENT": False,
            "OFFER_NAME": "Product",
            "OFFER_TAGS": "",
            "OFFER_TOKEN": "N2XPV5",
            "OFFER_WITHDRAWAL_DELAY": None,
            "OFFER_WITHDRAWAL_DETAILS": None,
            "OFFER_WITHDRAWAL_TYPE": None,
            "QR_CODE": "PASSCULTURE:v3;TOKEN:N2XPV5",
            "SUBCATEGORY": "SEANCE_CINE",
            "USER_FIRST_NAME": "Jeanne",
            "VENUE_ADDRESS": "1 boulevard Poissonnière",
            "VENUE_CITY": "Paris",
            "VENUE_NAME": "Le Petit Rintintin",
            "VENUE_POSTAL_CODE": "75000",
        }

    def should_return_event_specific_data_for_email_when_offer_is_a_duo_event(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(),
            quantity=2,
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["IS_DUO_EVENT"] is True

    def should_return_withdrawal_details_when_available(self):
        withdrawal_details = "Conditions de retrait spécifiques."
        booking = BookingFactory(stock=offers_factories.EventStockFactory(offer__withdrawalDetails=withdrawal_details))

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["OFFER_WITHDRAWAL_DETAILS"] == withdrawal_details

    def test_should_return_offer_tags(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__criteria=[criteria_factories.CriterionFactory(name="Tagged_offer")]
            )
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["OFFER_TAGS"] == "Tagged_offer"

    def should_use_venue_public_name_when_available(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__publicName="Cinéma du bout de la rue",
                offer__venue__name="Nom administratif du cinéma",
                offer__offererAddress=None,
            )
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["VENUE_NAME"] == "Cinéma du bout de la rue"

    def should_use_venue_name_when_public_name_is_unavailable(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__publicName=None,
                offer__venue__name="Cinéma du bout de la rue",
                offer__offererAddress=None,
            )
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["VENUE_NAME"] == "Cinéma du bout de la rue"

    def should_use_activation_code_when_available(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(),
        )
        offers_factories.ActivationCodeFactory(stock=booking.stock, booking=booking, code="AZ3")

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["OFFER_TOKEN"] == "AZ3"

    def should_format_withdrawal_delay_when_a_delay_is_set(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(offer__withdrawalDelay=60 * 60 * 24 * 2),
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data.params["OFFER_WITHDRAWAL_DELAY"] == "2 jours"

    def should_not_send_data_when_there_is_no_beginning_datetime(self):
        booking = BookingFactory(
            stock=offers_factories.EventStockFactory(
                beginningDatetime=None,
                bookingLimitDatetime=None,
            ),
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking)

        assert email_data is None
