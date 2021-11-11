from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.scripts.educational.update_educational_institutions_deposits import _process_educational_csv
from pcapi.scripts.educational.update_educational_institutions_deposits import update_educational_institutions_deposits


@pytest.mark.usefixtures("db_session")
class UpdateEducationalInstitutionsDepositsTest:
    @freeze_time("2020-11-17 15:00:00")
    def test_update_educational_institutions_deposits(self):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )
        educational_institution1 = factories.EducationalInstitutionFactory(institutionId="0790032L")
        deposit1 = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution1,
            educationalYear=educational_year,
            amount=500,
            isFinal=False,
        )

        educational_institution2 = factories.EducationalInstitutionFactory(institutionId="1790032L")
        deposit2 = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=600,
            isFinal=False,
        )

        # When
        update_educational_institutions_deposits("update_deposits.csv", "tests/scripts/educational/fixtures")

        # Then
        educational_institutions = models.EducationalInstitution.query.all()
        assert len(educational_institutions) == 2

        educational_deposits = models.EducationalDeposit.query.all()
        assert len(educational_deposits) == 2

        educational_deposit1 = models.EducationalDeposit.query.get(deposit1.id)
        assert educational_deposit1.isFinal is True
        assert educational_deposit1.amount == 6000

        educational_deposit2 = models.EducationalDeposit.query.get(deposit2.id)
        assert educational_deposit2.isFinal is True
        assert educational_deposit2.amount == 9000

    @freeze_time("2020-11-17 15:00:00")
    def test_update_institutions_deposits_with_institution_missing_ceases_execution(self):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )
        educational_institution = factories.EducationalInstitutionFactory(institutionId="1790032L")
        educational_deposit = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=500,
            isFinal=False,
        )

        # When
        _process_educational_csv(
            [
                {"UAICode": "0790032L", "depositAmount": 3000},
                {"UAICode": "1790032L", "depositAmount": 3000},
            ]
        )

        # Then
        educational_deposit = models.EducationalDeposit.query.filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution.id,
            models.EducationalDeposit.educationalYearId == educational_year.adageId,
        ).one()
        assert educational_deposit.amount == Decimal(500)

    @freeze_time("2020-11-17 15:00:00")
    def test_update_institutions_deposits_with_institution_deposit_missing_ceases_execution(self):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )

        factories.EducationalInstitutionFactory(institutionId="4790032L")
        educational_institution2 = factories.EducationalInstitutionFactory(institutionId="1790032L")
        educational_deposit = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=500,
            isFinal=False,
        )

        # When
        _process_educational_csv(
            [
                {"UAICode": "4790032L", "depositAmount": 5000},
                {"UAICode": "1790032L", "depositAmount": 3000},
            ]
        )

        # Then
        educational_deposit = models.EducationalDeposit.query.filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution2.id,
            models.EducationalDeposit.educationalYearId == educational_year.adageId,
        ).one()
        assert educational_deposit.amount == Decimal(500)

    @freeze_time("2020-11-17 15:00:00")
    def test_update_institutions_deposits_with_educational_year_missing_ceases_execution(self):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2018, 9, 1),
            expirationDate=datetime(2019, 8, 30),
        )
        educational_institution = factories.EducationalInstitutionFactory(institutionId="0790032L")
        educational_deposit = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=500,
            isFinal=False,
        )

        # When
        update_educational_institutions_deposits("update_deposits.csv", "tests/scripts/educational/fixtures")

        # Then
        deposit1 = models.EducationalDeposit.query.get(educational_deposit.id)
        assert deposit1.amount == 500
        assert deposit1.isFinal == False

    @freeze_time("2020-11-17 15:00:00")
    def test_stop_execution_when_csv_is_invalid(self):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )
        educational_institution = factories.EducationalInstitutionFactory(institutionId="0790032L")
        educational_deposit = factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=500,
            isFinal=False,
        )

        # When
        update_educational_institutions_deposits("invalid.csv", "tests/scripts/educational/fixtures")

        # Then
        deposit = models.EducationalDeposit.query.get(educational_deposit.id)
        assert deposit.amount == 500
