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
            educationalDeposit=educational_deposit,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            2,
            collectiveStock__price=Decimal(200.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )

        # available amount is
        # 1400
        # - 2 x 200 (2 confirmed bookings)
        # - 400 (confirmed booking)
        # - 400 (used booking)
        # = 200
        check_institution_fund(booking_amount=Decimal(200.00), deposit=educational_deposit)

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(booking_amount=Decimal(201.00), deposit=educational_deposit)

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
            educationalDeposit=educational_deposit,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )

        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(booking_amount=Decimal(200.00), deposit=educational_deposit)

    def test_institution_fund_is_insufficient(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
        )

        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(booking_amount=Decimal(200.00), deposit=educational_deposit)

    def test_check_deposit_not_final(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=False,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            2,
            collectiveStock__price=Decimal(125),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )

        # remaining year amount is (400 x 0.8) - 250 = 70
        # amount 69 -> ok
        check_institution_fund(booking_amount=Decimal(69), deposit=educational_deposit)
        # amount 71 -> raise
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(booking_amount=Decimal(71), deposit=educational_deposit)

    def test_check_deposit_final(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=True,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            2,
            collectiveStock__price=Decimal(125),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=educational_deposit,
        )

        # remaining year amount is 400 - 250 = 150
        # amount 149 -> ok
        check_institution_fund(booking_amount=Decimal(149), deposit=educational_deposit)
        # amount 151 -> raise
        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(booking_amount=Decimal(151), deposit=educational_deposit)
