import datetime
from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.validation import check_institution_fund


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="base_data", scope="class")
def base_data_fixture():
    educational_institution = EducationalInstitutionFactory()
    educational_year = EducationalYearFactory(adageId="1")

    # 50 confirmed booking amount in first period
    ConfirmedCollectiveBookingFactory.create_batch(
        5,
        collectiveStock__price=Decimal(10),
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        collectiveStock__endDatetime=datetime.datetime(year=educational_year.beginningDate.year, month=10, day=1),
    )
    # 200 confirmed booking amount in second period
    ConfirmedCollectiveBookingFactory.create_batch(
        20,
        collectiveStock__price=Decimal(10),
        educationalInstitution=educational_institution,
        educationalYear=educational_year,
        collectiveStock__endDatetime=datetime.datetime(year=educational_year.beginningDate.year + 1, month=2, day=1),
    )

    return educational_institution, educational_year


class EducationalValidationTest:
    def test_institution_fund_is_ok(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
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
            booking_date=datetime.datetime.utcnow(),
            deposit=educational_deposit,
        )

    def test_institution_fund_is_temporary_insufficient(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
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
                booking_date=datetime.datetime.utcnow(),
                deposit=educational_deposit,
            )

    def test_institution_fund_is_insufficient(self):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
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
                booking_date=datetime.datetime.utcnow(),
                deposit=educational_deposit,
            )

    def test_with_ratio_not_final(self, base_data):
        educational_institution, educational_year = base_data
        year = educational_year.beginningDate.year
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=False,
            creditRatio=Decimal(0.25),
        )

        # remaining first period amount is (400 x 0.25) - 50 = 50

        # amount 49 in first period -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(49),
            booking_date=datetime.datetime(year=year, month=10, day=1),
            deposit=educational_deposit,
        )
        # amount 51 in first period -> raise
        with pytest.raises(exceptions.InsufficientFundFirstPeriod):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(51),
                booking_date=datetime.datetime(year=year, month=10, day=1),
                deposit=educational_deposit,
            )

        # remaining year amount is (400 x 0.8) - 250 = 70

        # amount 69 in second period -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(69),
            booking_date=datetime.datetime(year=year + 1, month=2, day=1),
            deposit=educational_deposit,
        )
        # amount 71 in second period -> raise
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(71),
                booking_date=datetime.datetime(year=year + 1, month=2, day=1),
                deposit=educational_deposit,
            )

    def test_with_ratio_final(self, base_data):
        educational_institution, educational_year = base_data
        year = educational_year.beginningDate.year
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=True,
            creditRatio=Decimal(0.25),
        )

        # remaining first period amount is (400 x 0.25) - 50 = 50

        # amount 49 in first period -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(49),
            booking_date=datetime.datetime(year=year, month=10, day=1),
            deposit=educational_deposit,
        )
        # amount 51 in first period -> raise
        with pytest.raises(exceptions.InsufficientFundFirstPeriod):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(51),
                booking_date=datetime.datetime(year=year, month=10, day=1),
                deposit=educational_deposit,
            )

        # remaining year amount is 400 - 250 = 150

        # amount 149 in second period -> ok
        check_institution_fund(
            educational_institution_id=educational_institution.id,
            educational_year_id=educational_year.adageId,
            booking_amount=Decimal(149),
            booking_date=datetime.datetime(year=year + 1, month=2, day=1),
            deposit=educational_deposit,
        )
        # amount 151 in second period -> raise
        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(151),
                booking_date=datetime.datetime(year=year + 1, month=2, day=1),
                deposit=educational_deposit,
            )

    def test_without_ratio_not_final(self, base_data):
        educational_institution, educational_year = base_data
        year = educational_year.beginningDate.year
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=False,
            creditRatio=None,
        )

        # remaining year amount is (400 x 0.8) - 250 = 70
        # creditRatio is None so the result is the same for both periods

        for booking_date in (
            datetime.datetime(year=year, month=10, day=1),
            datetime.datetime(year=year + 1, month=2, day=1),
        ):
            # amount 69 -> ok
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(69),
                booking_date=booking_date,
                deposit=educational_deposit,
            )
            # amount 71 -> raise
            with pytest.raises(exceptions.InsufficientTemporaryFund):
                check_institution_fund(
                    educational_institution_id=educational_institution.id,
                    educational_year_id=educational_year.adageId,
                    booking_amount=Decimal(71),
                    booking_date=booking_date,
                    deposit=educational_deposit,
                )

    def test_without_ratio_final(self, base_data):
        educational_institution, educational_year = base_data
        year = educational_year.beginningDate.year
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400),
            isFinal=True,
            creditRatio=None,
        )

        # remaining year amount is 400 - 250 = 150
        # creditRatio is None so the result is the same for both periods

        for booking_date in (
            datetime.datetime(year=year, month=10, day=1),
            datetime.datetime(year=year + 1, month=2, day=1),
        ):
            # amount 149 -> ok
            check_institution_fund(
                educational_institution_id=educational_institution.id,
                educational_year_id=educational_year.adageId,
                booking_amount=Decimal(149),
                booking_date=booking_date,
                deposit=educational_deposit,
            )
            # amount 151 -> raise
            with pytest.raises(exceptions.InsufficientFund):
                check_institution_fund(
                    educational_institution_id=educational_institution.id,
                    educational_year_id=educational_year.adageId,
                    booking_amount=Decimal(151),
                    booking_date=booking_date,
                    deposit=educational_deposit,
                )
