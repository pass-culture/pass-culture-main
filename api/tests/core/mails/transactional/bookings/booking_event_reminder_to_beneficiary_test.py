import dataclasses

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    get_booking_event_reminder_to_beneficiary_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    send_individual_booking_event_reminder_email_to_beneficiary,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


def get_expected_base_sendinblue_email_data(individual_booking, **overrides):
    email_data = SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY.value,
        params={
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{individual_booking.booking.id}/details",
            "EVENT_DATE": "20 octobre 2021",
            "EVENT_HOUR": "14h48",
            "OFFER_NAME": individual_booking.booking.stock.offer.name,
            "OFFER_TOKEN": individual_booking.booking.token,
            "OFFER_WITHDRAWAL_DELAY": None,
            "OFFER_WITHDRAWAL_DETAILS": None,
            "OFFER_WITHDRAWAL_TYPE": None,
            "QR_CODE": bookings_api.get_qr_code_data(individual_booking.booking.token),
            "IS_DUO_EVENT": False,
            "SUBCATEGORY": "SEANCE_CINE",
            "USER_FIRST_NAME": individual_booking.user.firstName,
            "VENUE_ADDRESS": individual_booking.booking.stock.offer.venue.address,
            "VENUE_CITY": individual_booking.booking.stock.offer.venue.city,
            "VENUE_NAME": individual_booking.booking.stock.offer.venue.name,
            "VENUE_POSTAL_CODE": individual_booking.booking.stock.offer.venue.postalCode,
        },
    )
    email_data.params.update(overrides)
    return email_data


@freeze_time("2021-10-15 12:48:00")
class SendIndividualBookingEventReminderEmailToBeneficiaryTest:
    def test_sendinblue_send_email(self):
        booking = IndividualBookingFactory(stock=offers_factories.EventStockFactory())

        send_individual_booking_event_reminder_email_to_beneficiary(booking.individualBooking)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY.value
        )


@freeze_time("2021-10-15 12:48:00")
class GetBookingEventReminderToBeneficiaryEmailDataTest:
    def given_nominal_booking_event(self):
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__name="Le Petit Rintintin",
                offer__name="Product",
            ),
            token="N2XPV5",
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params == {
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
            "EVENT_DATE": "20 octobre 2021",
            "EVENT_HOUR": "14h48",
            "IS_DUO_EVENT": False,
            "OFFER_NAME": "Product",
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
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(),
            quantity=2,
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["IS_DUO_EVENT"] is True

    def should_return_withdrawal_details_when_available(self):
        withdrawal_details = "Conditions de retrait spécifiques."
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(offer__withdrawalDetails=withdrawal_details)
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["OFFER_WITHDRAWAL_DETAILS"] == withdrawal_details

    def should_use_venue_public_name_when_available(self):
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__publicName="Cinéma du bout de la rue",
                offer__venue__name="Nom administratif du cinéma",
            )
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["VENUE_NAME"] == "Cinéma du bout de la rue"

    def should_use_venue_name_when_public_name_is_unavailable(self):
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue__publicName=None,
                offer__venue__name="Cinéma du bout de la rue",
            )
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["VENUE_NAME"] == "Cinéma du bout de la rue"

    def should_use_activation_code_when_available(self):
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(),
        )
        offers_factories.ActivationCodeFactory(stock=booking.stock, booking=booking, code="AZ3")

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["OFFER_TOKEN"] == "AZ3"

    def should_format_withdrawal_delay_when_a_delay_is_set(self):
        booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(offer__withdrawalDelay=60 * 60 * 24 * 2),
        )

        email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

        assert email_data.params["OFFER_WITHDRAWAL_DELAY"] == "2 jours"
