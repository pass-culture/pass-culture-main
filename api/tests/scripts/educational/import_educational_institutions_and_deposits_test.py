from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.scripts.educational.import_educational_institutions_and_deposits import (
    import_educational_institutions_and_deposits,
)
from pcapi.scripts.educational.import_educational_institutions_and_deposits import _process_educational_csv


class ImportEducationalInstitutionTest:
    @freeze_time("2020-11-17 15:00:00")
    def test_import_educational_institutions_and_deposits(self, db_session):
        # Given
        factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )

        # When
        import_educational_institutions_and_deposits(
            "institutions_and_deposits.csv", "tests/scripts/educational/fixtures"
        )

        # Then
        educational_institutions = models.EducationalInstitution.query.all()
        assert len(educational_institutions) == 5

        educational_deposits = models.EducationalDeposit.query.all()
        assert len(educational_deposits) == 5
        assert all(not educational_deposit.isFinal for educational_deposit in educational_deposits)

    @freeze_time("2020-11-17 15:00:00")
    def test_import_educational_institutions_and_deposits_with_existing_data_on_current_year(self, db_session):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )
        educational_institution = factories.EducationalInstitutionFactory(institutionId="3790032L")
        factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=500,
        )

        # When
        _process_educational_csv([{"UAICode": "3790032L", "depositAmount": 3000}])

        # Then it does not update educational deposit or create one if it exists for current year
        educational_deposit = models.EducationalDeposit.query.filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution.id,
            models.EducationalDeposit.educationalYearId == educational_year.adageId,
        ).one()
        assert educational_deposit.amount == Decimal(500)

    @freeze_time("2020-11-17 15:00:00")
    def test_import_educational_institutions_and_deposits_with_existing_data_on_future_year(self, db_session):
        # Given
        educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2020, 9, 1),
            expirationDate=datetime(2021, 8, 30),
        )
        future_educational_year = factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1),
            expirationDate=datetime(2022, 8, 30),
        )

        educational_institution2 = factories.EducationalInstitutionFactory(institutionId="4790032L")
        factories.EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=future_educational_year,
        )

        # When
        _process_educational_csv([{"UAICode": "4790032L", "depositAmount": 5000}])

        # Then it creates educational deposit for current year even if it exists for another year
        educational_deposit = models.EducationalDeposit.query.filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution2.id,
            models.EducationalDeposit.educationalYearId == educational_year.adageId,
        ).one()
        assert educational_deposit.amount == Decimal(5000)

    @freeze_time("2020-11-17 15:00:00")
    def test_stop_execution_when_no_educational_year_found(self):
        # When
        import_educational_institutions_and_deposits(
            "institutions_and_deposits.csv", "tests/scripts/educational/fixtures"
        )

        # Then
        educational_institutions = models.EducationalInstitution.query.all()
        assert len(educational_institutions) == 0

        educational_deposits = models.EducationalDeposit.query.all()
        assert len(educational_deposits) == 0

    @freeze_time("2020-11-17 15:00:00")
    def test_stop_execution_when_csv_is_invalid(self):
        # When
        import_educational_institutions_and_deposits("invalid.csv", "tests/scripts/educational/fixtures")

        # Then
        educational_institutions = models.EducationalInstitution.query.all()
        assert len(educational_institutions) == 0

        educational_deposits = models.EducationalDeposit.query.all()
        assert len(educational_deposits) == 0
