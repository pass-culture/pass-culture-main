from decimal import Decimal

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.repository import get_confirmed_educational_bookings_amount


class EducationalRepositoryTest:
    def test_get_not_cancelled_educational_bookings_amount(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        another_educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        another_educational_year = EducationalYearFactory(adageId="2")
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
        )
        EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )
        EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.USED,
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
        )
        EducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CANCELLED,
            isCancelled=True,
        )
        EducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=another_educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )
        EducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=another_educational_year,
            status=BookingStatus.CONFIRMED,
        )

        total_amount = get_confirmed_educational_bookings_amount(educational_institution.id, educational_year.adageId)
        assert total_amount == Decimal(1200.00)
