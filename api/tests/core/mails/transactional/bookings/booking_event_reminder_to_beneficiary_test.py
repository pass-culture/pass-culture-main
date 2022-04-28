import dataclasses
from datetime import datetime

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


@freeze_time("2021-10-15 12:48:00")
def test_sendinblue_send_email():
    booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=1.99), dateCreated=datetime.utcnow()
    )
    send_individual_booking_event_reminder_email_to_beneficiary(booking.individualBooking)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
        TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY.value
    )


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
def test_should_return_event_specific_data_for_email_when_offer_is_an_event():
    booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow()
    )
    email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)
    expected = get_expected_base_sendinblue_email_data(booking.individualBooking)
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_event_specific_data_for_email_when_offer_is_a_duo_event():
    booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow(), quantity=2
    )

    email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking.individualBooking,
        IS_DUO_EVENT=True,
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_use_public_name_when_available():
    booking = IndividualBookingFactory(
        dateCreated=datetime.utcnow(),
        stock=offers_factories.EventStockFactory(
            price=23.99,
            offer__venue__name="LIBRAIRIE GENERALE UNIVERSITAIRE COLBERT",
            offer__venue__publicName="Librairie Colbert",
        ),
    )

    email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking.individualBooking,
        VENUE_NAME="Librairie Colbert",
        **{key: value for key, value in email_data.params.items() if key != "VENUE_NAME"},
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_withdrawal_details_when_available():
    withdrawal_details = "Conditions de retrait spécifiques."
    booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99, offer__withdrawalDetails=withdrawal_details),
        dateCreated=datetime.utcnow(),
    )

    email_data = get_booking_event_reminder_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking.individualBooking,
        OFFER_WITHDRAWAL_DETAILS=withdrawal_details,
        **{key: value for key, value in email_data.params.items() if key != "OFFER_WITHDRAWAL_DETAILS"},
    )
    assert email_data == expected
