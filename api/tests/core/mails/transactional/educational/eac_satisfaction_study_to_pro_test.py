from dataclasses import asdict
import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.educational import factories as educational_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.educational.eac_satisfaction_study_to_pro import (
    send_eac_satisfaction_study_email_to_pro,
)
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

    booking = bookings_factories.EducationalBookingFactory(
        educationalBooking__educationalInstitution=educational_institution,
        educationalBooking__educationalRedactor=educational_redactor,
        stock__beginningDatetime=datetime.datetime(2021, 5, 15),
    )

    educational_booking = booking.educationalBooking

    # When
    send_eac_satisfaction_study_email_to_pro(educational_booking)

    # Then
    assert len(mails_testing.outbox) == 1
    sent_data = mails_testing.outbox[0].sent_data
    offer = educational_booking.booking.stock.offer
    assert sent_data["To"] == offer.venue.bookingEmail
    assert sent_data["template"] == asdict(TransactionalEmail.EAC_SATISFACTION_STUDY_TO_PRO.value)
    assert sent_data["params"] == {
        "OFFER_NAME": offer.name,
        "VENUE_NAME": offer.venue.name,
        "EVENT_DATE": "samedi 15 mai 2021",
        "REDACTOR_FIRSTNAME": "Georges",
        "REDACTOR_LASTNAME": "Moustaki",
        "REDACTOR_EMAIL": "professeur@example.com",
        "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
        "EDUCATIONAL_INSTITUTION_CITY": "Paris",
        "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
    }
