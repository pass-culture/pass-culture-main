import logging
from datetime import timedelta
from decimal import Decimal
from tempfile import NamedTemporaryFile

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import utils
from pcapi.core.educational.api.institution import ImportDepositPeriodOption
from pcapi.core.educational.api.institution import import_deposit_institution_csv
from pcapi.core.educational.api.institution import import_deposit_institution_data
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


def _get_deposit(year, institution) -> educational_models.EducationalDeposit:
    return (
        db.session.query(educational_models.EducationalDeposit)
        .filter(
            educational_models.EducationalDeposit.educationalInstitution == institution,
            educational_models.EducationalDeposit.educationalYear == year,
        )
        .populate_existing()
        .one()
    )


class ImportDepositInstitutionDataTest:
    def test_create_institution(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="replace",
            ministry_conflict="keep",
            final=False,
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = _get_deposit(ansco, institution)

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive is True

        assert deposit.amount == Decimal(1250)
        assert deposit.dateCreated - date_utils.get_naive_utc_now() < timedelta(seconds=5)
        assert deposit.isFinal is False
        assert deposit.ministry == educational_models.Ministry.EDUCATION_NATIONALE
        assert deposit.period.lower == ansco.beginningDate
        assert deposit.period.upper == ansco.expirationDate

    def test_update_institution(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="replace",
            ministry_conflict="keep",
            final=False,
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = _get_deposit(ansco, institution)

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive is True

        assert deposit.amount == Decimal(1250)
        assert deposit.dateCreated - date_utils.get_naive_utc_now() < timedelta(seconds=5)
        assert deposit.isFinal is False
        assert deposit.ministry == educational_models.Ministry.EDUCATION_NATIONALE
        assert deposit.period.lower == ansco.beginningDate
        assert deposit.period.upper == ansco.expirationDate

    def test_institution_not_in_adage(self):
        ansco = educational_factories.EducationalYearFactory()
        data = {"pouet": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=ansco,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                credit_update="replace",
                ministry_conflict="keep",
                final=False,
            )

        assert db.session.query(educational_models.EducationalInstitution).count() == 0
        assert db.session.query(educational_models.EducationalDeposit).count() == 0
        assert str(exception.value) == "UAIs not found in adage: ['pouet']"

    def test_deposit_alread_in_ministry_replace(self, caplog) -> None:
        ansco = educational_factories.EducationalYearFactory()
        old_institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=old_institution,
            educationalYear=ansco,
            ministry=educational_models.Ministry.AGRICULTURE,
        )
        data = {"0470010E": 1250}

        with caplog.at_level(logging.WARNING):
            import_deposit_institution_data(
                data=data,
                educational_year=ansco,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                credit_update="replace",
                ministry_conflict="replace",
                final=False,
            )

        [record] = caplog.records
        assert (
            record.message == f"Ministry changed from 'AGRICULTURE' to 'EDUCATION_NATIONALE' for deposit {deposit.id}"
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = _get_deposit(ansco, institution)

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive is True

        assert deposit.amount == Decimal(1250)
        assert deposit.isFinal is False
        assert deposit.ministry == educational_models.Ministry.EDUCATION_NATIONALE
        assert deposit.period.lower == ansco.beginningDate
        assert deposit.period.upper == ansco.expirationDate

    def test_deposit_alread_in_ministry_keep(self, caplog) -> None:
        ansco = educational_factories.EducationalYearFactory()
        old_institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=old_institution,
            educationalYear=ansco,
            ministry=educational_models.Ministry.AGRICULTURE,
        )
        data = {"0470010E": 1250}

        with caplog.at_level(logging.WARNING):
            import_deposit_institution_data(
                data=data,
                educational_year=ansco,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                credit_update="replace",
                ministry_conflict="keep",
                final=False,
            )

        [record] = caplog.records
        assert record.message == f"Kept previous ministry 'AGRICULTURE' for deposit {deposit.id}"

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = _get_deposit(ansco, institution)

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive is True

        assert deposit.amount == Decimal(1250)
        assert deposit.isFinal is False
        assert deposit.ministry == educational_models.Ministry.AGRICULTURE
        assert deposit.period.lower == ansco.beginningDate
        assert deposit.period.upper == ansco.expirationDate

    def test_import_csv(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        uai = "0470010E"
        new_uai = "0470009E"
        educational_factories.EducationalInstitutionFactory(institutionId=uai)

        content = f"""UAI;Crédits de dépenses
        {uai};1250
        {new_uai};1500"""

        with NamedTemporaryFile(mode="w") as tmp:
            tmp.write(content)
            tmp.flush()

            with open(tmp.name) as f:
                import_deposit_institution_csv(
                    path=f.name,
                    year=ansco.beginningDate.year,
                    ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                    period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                    credit_update="replace",
                    ministry_conflict="replace",
                    program_name=None,
                    final=False,
                )

        institution = db.session.query(educational_models.EducationalInstitution).filter_by(institutionId=uai).one()
        new_institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId=new_uai).one()
        )
        deposit = _get_deposit(ansco, institution)
        deposit_new_uai = _get_deposit(ansco, new_institution)

        assert institution.institutionId == uai
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive is True

        assert new_institution.institutionId == new_uai
        assert new_institution.institutionType == "COLLEGE"
        assert new_institution.name == "DE LA TOUR0"
        assert new_institution.city == "PARIS"
        assert new_institution.postalCode == "75000"
        assert new_institution.email == "contact+collegelatour@example.com"
        assert new_institution.phoneNumber == "0600000000"
        assert new_institution.isActive is True

        assert deposit.amount == Decimal(1250)
        assert deposit.dateCreated - date_utils.get_naive_utc_now() < timedelta(seconds=5)
        assert deposit.isFinal is False
        assert deposit.ministry == educational_models.Ministry.EDUCATION_NATIONALE
        assert deposit.period.lower == ansco.beginningDate
        assert deposit.period.upper == ansco.expirationDate

        assert deposit_new_uai.amount == Decimal(1500)
        assert deposit_new_uai.dateCreated - date_utils.get_naive_utc_now() < timedelta(seconds=5)
        assert deposit_new_uai.isFinal is False
        assert deposit_new_uai.ministry == educational_models.Ministry.EDUCATION_NATIONALE
        assert deposit_new_uai.period.lower == ansco.beginningDate
        assert deposit_new_uai.period.upper == ansco.expirationDate


class ImportDepositPeriodTest:
    @pytest.mark.parametrize("with_existing_deposit", (True, False))
    def test_deposit_educational_year(self, with_existing_deposit):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        if with_existing_deposit:
            educational_factories.EducationalDepositFactory(educationalInstitution=institution, educationalYear=year)
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(1250)

    def test_deposit_educational_year_overlap_error(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit = educational_factories.EducationalDepositFirstPeriodFactory(
            educationalInstitution=institution, educationalYear=year
        )
        data = {"0470010E": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=year,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                credit_update="replace",
                ministry_conflict="keep",
                final=True,
            )

        assert (
            str(exception.value)
            == f"Deposit with id {deposit.id} has a period that overlaps (and is different from) input period"
        )
        # check that deposit has not changed
        assert db.session.query(educational_models.EducationalDeposit).one() == deposit
        assert deposit.period.lower, deposit.period.upper == utils.get_educational_year_first_period_bounds(year)
        assert deposit.amount == Decimal(3000)

    def test_deposit_educational_year_overlap_two_periods_error(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit_first_period = educational_factories.EducationalDepositFirstPeriodFactory(
            educationalInstitution=institution, educationalYear=year
        )
        deposit_second_period = educational_factories.EducationalDepositSecondPeriodFactory(
            educationalInstitution=institution, educationalYear=year
        )
        data = {"0470010E": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=year,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
                credit_update="replace",
                ministry_conflict="keep",
                final=True,
            )

        assert str(exception.value) == "Found 2 deposits that overlap input period"
        # check that deposits have not changed
        assert (
            deposit_first_period.period.lower,
            deposit_first_period.period.upper,
        ) == utils.get_educational_year_first_period_bounds(year)
        assert deposit_first_period.amount == Decimal(3000)

        assert (
            deposit_second_period.period.lower,
            deposit_second_period.period.upper,
        ) == utils.get_educational_year_second_period_bounds(year)
        assert deposit_second_period.amount == Decimal(3000)

    @pytest.mark.parametrize("with_existing_deposit", (True, False))
    def test_deposit_first_period(self, with_existing_deposit):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        if with_existing_deposit:
            educational_factories.EducationalDepositFirstPeriodFactory(
                educationalInstitution=institution, educationalYear=year
            )
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FIRST_PERIOD,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower, deposit.period.upper == utils.get_educational_year_first_period_bounds(year)
        assert deposit.amount == Decimal(1250)

    def test_deposit_first_period_overlap_error(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=institution, educationalYear=year
        )
        data = {"0470010E": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=year,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FIRST_PERIOD,
                credit_update="replace",
                ministry_conflict="keep",
                final=True,
            )

        assert (
            str(exception.value)
            == f"Deposit with id {deposit.id} has a period that overlaps (and is different from) input period"
        )
        # check that deposit has not changed
        assert db.session.query(educational_models.EducationalDeposit).one() == deposit
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(3000)

    @pytest.mark.parametrize("with_existing_deposit", (True, False))
    def test_deposit_second_period(self, with_existing_deposit):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        if with_existing_deposit:
            educational_factories.EducationalDepositSecondPeriodFactory(
                educationalInstitution=institution, educationalYear=year
            )
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_SECOND_PERIOD,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower, deposit.period.upper == utils.get_educational_year_second_period_bounds(year)
        assert deposit.amount == Decimal(1250)

    def test_deposit_second_period_overlap_error(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=institution, educationalYear=year
        )
        data = {"0470010E": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=year,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_SECOND_PERIOD,
                credit_update="replace",
                ministry_conflict="keep",
                final=True,
            )

        assert (
            str(exception.value)
            == f"Deposit with id {deposit.id} has a period that overlaps (and is different from) input period"
        )
        # check that deposit has not changed
        assert db.session.query(educational_models.EducationalDeposit).one() == deposit
        assert deposit.period.lower, deposit.period.upper == utils.get_educational_year_first_period_bounds(year)
        assert deposit.amount == Decimal(3000)

    @pytest.mark.parametrize("with_existing_deposit", (True, False))
    def test_deposit_second_period_with_previous_period_in_db(self, with_existing_deposit):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        if with_existing_deposit:
            educational_factories.EducationalDepositSecondPeriodFactory(
                educationalInstitution=institution, educationalYear=year
            )
        educational_factories.EducationalDepositFirstPeriodFactory(
            educationalInstitution=institution, educationalYear=year
        )
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_SECOND_PERIOD,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        deposits = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitution == institution,
                educational_models.EducationalDeposit.educationalYear == year,
            )
            .populate_existing()
            .order_by(educational_models.EducationalDeposit.period)
        )
        deposit_first_period, deposit_second_period = deposits
        assert (
            deposit_first_period.period.lower,
            deposit_first_period.period.upper,
        ) == utils.get_educational_year_first_period_bounds(year)

        assert (
            deposit_second_period.period.lower,
            deposit_second_period.period.upper,
        ) == utils.get_educational_year_second_period_bounds(year)
        assert deposit_second_period.amount == Decimal(1250)


class ImportDepositCreditUpdateTest:
    def test_import_replace(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")

        data = {"0470010E": 1250}

        output = import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        assert output.total_previous_deposit == 0
        assert output.total_imported_amount == 1250
        assert output.total_new_deposit == 1250

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(1250)

    def test_import_replace_with_existing_deposit(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=institution, educationalYear=year, amount=Decimal(2000)
        )

        data = {"0470010E": 1250}

        output = import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="replace",
            ministry_conflict="keep",
            final=True,
        )

        assert output.total_previous_deposit == 2000
        assert output.total_imported_amount == 1250
        assert output.total_new_deposit == 1250

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(1250)

    def test_import_add(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")

        data = {"0470010E": 1250}

        output = import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="add",
            ministry_conflict="keep",
            final=True,
        )

        assert output.total_previous_deposit == 0
        assert output.total_imported_amount == 1250
        assert output.total_new_deposit == 1250

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(1250)

    def test_import_add_with_existing_deposit(self):
        year = educational_factories.EducationalYearFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=institution, educationalYear=year, amount=Decimal(2000)
        )

        data = {"0470010E": 1250}

        output = import_deposit_institution_data(
            data=data,
            educational_year=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FULL,
            credit_update="add",
            ministry_conflict="keep",
            final=True,
        )

        assert output.total_previous_deposit == 2000
        assert output.total_imported_amount == 1250
        assert output.total_new_deposit == 3250

        deposit = _get_deposit(year, institution)
        assert deposit.period.lower == year.beginningDate
        assert deposit.period.upper == year.expirationDate
        assert deposit.amount == Decimal(3250)
