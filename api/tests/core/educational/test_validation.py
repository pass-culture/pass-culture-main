import datetime
from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.validation import check_institution_fund


pytestmark = pytest.mark.usefixtures("db_session")


def _generate_bookings(deposit, institution, year) -> None:
    # 50 confirmed booking amount in first period
    ConfirmedCollectiveBookingFactory.create_batch(
        2,
        collectiveStock__price=Decimal(25),
        educationalInstitution=institution,
        educationalYear=year,
        educationalDeposit=deposit,
        collectiveStock__endDatetime=datetime.datetime(year=year.beginningDate.year, month=10, day=1),
    )
    # 200 confirmed booking amount in second period
    ConfirmedCollectiveBookingFactory.create_batch(
        2,
        collectiveStock__price=Decimal(100),
        educationalInstitution=institution,
        educationalYear=year,
        educationalDeposit=deposit,
        collectiveStock__endDatetime=datetime.datetime(year=year.beginningDate.year + 1, month=2, day=1),
    )


class EducationalValidationTest:
    def test_institution_fund_is_ok(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
        )

        PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        CancelledCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            20,
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(200.00),
            deposit=educational_deposit,
        )

    def test_institution_fund_is_temporary_insufficient(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=False,
        )

        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(200.00),
                deposit=educational_deposit,
            )

    def test_institution_fund_is_insufficient(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
        )

        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(200.00),
                deposit=educational_deposit,
            )

    def test_check_deposit_not_final(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=False,
        )
        _generate_bookings(educational_deposit, educational_institution, educational_year)

        # remaining year amount is (400 x 0.8) - 250 = 70
        # amount 69 -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(69),
            deposit=educational_deposit,
        )
        # amount 71 -> raise
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(71),
                deposit=educational_deposit,
            )

    def test_check_deposit_final(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=True,
        )
        _generate_bookings(educational_deposit, educational_institution, educational_year)

        # remaining year amount is 400 - 250 = 150
        # amount 149 -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(149),
            deposit=educational_deposit,
        )
        # amount 151 -> raise
        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(151),
                deposit=educational_deposit,
            )
