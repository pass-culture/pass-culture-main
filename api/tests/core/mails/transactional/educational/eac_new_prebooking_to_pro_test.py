from dataclasses import asdict
import datetime
from decimal import Decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import factories as educational_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.educational.eac_new_prebooking_to_pro import get_eac_new_prebooking_email_data
from pcapi.core.mails.transactional.educational.eac_new_prebooking_to_pro import send_eac_new_prebooking_email_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


def test_sends_email():
    # Given
    educational_redactor = educational_factories.EducationalRedactorFactory(
        email="professeur@example.com", firstName="Georges", lastName="Moustaki"
    )
    educational_institution = educational_factories.EducationalInstitutionFactory(
        name="Lycée du pass", city="Paris", postalCode="75018"
    )
    educational_year = educational_factories.EducationalYearFactory(adageId="1")
    educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        amount=Decimal(1000.00),
        isFinal=True,
    )
    booking = bookings_factories.EducationalBookingFactory(
        amount=Decimal(20.00),
        quantity=10,
        educationalBooking__educationalInstitution=educational_institution,
        educationalBooking__educationalYear=educational_year,
        educationalBooking__educationalRedactor=educational_redactor,
        status=BookingStatus.PENDING,
        stock__offer__bookingEmail="test@email.com",
        stock__beginningDatetime=datetime.datetime(2021, 5, 15),
    )

    # When
    send_eac_new_prebooking_email_to_pro(booking.stock, booking)

    # Then
    assert len(mails_testing.outbox) == 1
    sent_data = mails_testing.outbox[0].sent_data
    offer = booking.stock.offer
    assert sent_data["To"] == "test@email.com"
    assert sent_data["template"] == asdict(TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value)
    assert sent_data["params"] == {
        "OFFER_NAME": offer.name,
        "VENUE_NAME": offer.venue.name,
        "EVENT_DATE": "samedi 15 mai 2021",
        "EVENT_HOUR": "2h",
        "PRICE": "20.00",
        "QUANTITY": 10,
        "REDACTOR_FIRSTNAME": "Georges",
        "REDACTOR_LASTNAME": "Moustaki",
        "REDACTOR_EMAIL": "professeur@example.com",
        "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
        "EDUCATIONAL_INSTITUTION_CITY": "Paris",
        "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
        "IS_EVENT": True,
    }


def test_get_email_metadata():

    # Given
    educational_redactor = educational_factories.EducationalRedactorFactory(
        email="professeur@example.com", firstName="Georges", lastName="Moustaki"
    )
    educational_institution = educational_factories.EducationalInstitutionFactory(
        name="Lycée du pass", city="Paris", postalCode="75018"
    )
    educational_year = educational_factories.EducationalYearFactory(adageId="1")
    educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        amount=Decimal(1000.00),
        isFinal=True,
    )
    booking = bookings_factories.EducationalBookingFactory(
        amount=Decimal(20.00),
        quantity=10,
        educationalBooking__educationalInstitution=educational_institution,
        educationalBooking__educationalYear=educational_year,
        educationalBooking__educationalRedactor=educational_redactor,
        status=BookingStatus.PENDING,
        stock__offer__bookingEmail="test@email.com",
        stock__beginningDatetime=datetime.datetime(2021, 5, 15),
    )
    offer = booking.stock.offer

    # When
    email_data = get_eac_new_prebooking_email_data(booking)

    # Then

    assert email_data.template == TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value
    assert email_data.params == {
        "OFFER_NAME": offer.name,
        "VENUE_NAME": offer.venue.name,
        "EVENT_DATE": "samedi 15 mai 2021",
        "EVENT_HOUR": "2h",
        "PRICE": "20.00",
        "QUANTITY": 10,
        "REDACTOR_FIRSTNAME": "Georges",
        "REDACTOR_LASTNAME": "Moustaki",
        "REDACTOR_EMAIL": "professeur@example.com",
        "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
        "EDUCATIONAL_INSTITUTION_CITY": "Paris",
        "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
        "IS_EVENT": True,
    }
