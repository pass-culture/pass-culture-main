from decimal import Decimal

import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import exceptions
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.validation import check_institution_fund


class EducationalValidationTest:
    def test_institution_fund_is_ok(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
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

        check_institution_fund(
            educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
        )

    def test_institution_fund_is_temporary_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=False,
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
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

        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )

    def test_institution_fund_is_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
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

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )
