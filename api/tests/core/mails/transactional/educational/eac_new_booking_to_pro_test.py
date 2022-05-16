from dataclasses import asdict
import datetime
from decimal import Decimal
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import factories as educational_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import get_eac_new_booking_to_pro_email_data
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import send_eac_new_booking_email_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


class GetEacNewBookingEmailDataTest:
    def test_get_data_when_booking_price_equal_zero(self):
        # Given
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
            amount=Decimal(00.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalRedactor=educational_redactor,
            status=BookingStatus.PENDING,
            stock__offer__bookingEmail="test@email.com",
            stock__beginningDatetime=datetime.datetime(2021, 5, 15),
        )

        data = get_eac_new_booking_to_pro_email_data(booking)
        offer = booking.stock.offer
        assert data.params == {
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": "15-May-2021",
            "EVENT_HOUR": "2h",
            "QUANTITY": 1,
            "PRICE": "Gratuit",
            "REDACTOR_FIRSTNAME": "Georges",
            "REDACTOR_LASTNAME": "Moustaki",
            "REDACTOR_EMAIL": "professeur@example.com",
            "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
            "EDUCATIONAL_INSTITUTION_CITY": "Paris",
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
            "IS_EVENT": True,
        }


class SendEacNewBookingEmailToProTest:
    def test_sends_email(self):
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
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalRedactor=educational_redactor,
            status=BookingStatus.PENDING,
            stock__offer__bookingEmail="test@email.com",
            stock__beginningDatetime=datetime.datetime(2021, 5, 15),
        )

        # When
        send_eac_new_booking_email_to_pro(booking)

        # Then
        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data
        offer = booking.stock.offer
        assert sent_data["To"] == "test@email.com"
        assert sent_data["template"] == asdict(TransactionalEmail.EAC_NEW_BOOKING_TO_PRO.value)
        assert sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": "15-May-2021",
            "EVENT_HOUR": "2h",
            "QUANTITY": 1,
            "PRICE": "20.00 €",
            "REDACTOR_FIRSTNAME": "Georges",
            "REDACTOR_LASTNAME": "Moustaki",
            "REDACTOR_EMAIL": "professeur@example.com",
            "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
            "EDUCATIONAL_INSTITUTION_CITY": "Paris",
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
            "IS_EVENT": True,
        }

    @freeze_time("2019-11-26 18:29:20.891028")
    @patch("pcapi.core.mails.transactional.educational.eac_new_booking_to_pro.mails")
    def test_with_collective_booking(self, mails):
        # given
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__bookingEmail="pouet@example.com",
        )

        # when
        send_eac_new_booking_email_to_pro(booking)

        # then
        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "27-Nov-2019",
            "EVENT_HOUR": "19h29",
            "QUANTITY": 1,
            "PRICE": "100.00 €",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "IS_EVENT": True,
        }
