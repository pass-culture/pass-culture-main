from datetime import timedelta
from decimal import Decimal
from tempfile import NamedTemporaryFile

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api.institution import import_deposit_institution_csv
from pcapi.core.educational.api.institution import import_deposit_institution_data
from pcapi.models import db
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class ImportDepositInstitutionDataTest:
    def test_create_institution(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            final=False,
            conflict="crash",
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitution == institution,
                educational_models.EducationalDeposit.educationalYear == ansco,
            )
            .one()
        )

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

    def test_update_institution(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            final=False,
            conflict="crash",
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitution == institution,
                educational_models.EducationalDeposit.educationalYear == ansco,
            )
            .one()
        )

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

    def test_institution_not_in_adage(self):
        ansco = educational_factories.EducationalYearFactory()
        data = {"pouet": 1250}

        with pytest.raises(ValueError) as exception:
            import_deposit_institution_data(
                data=data,
                educational_year=ansco,
                ministry=educational_models.Ministry.EDUCATION_NATIONALE,
                final=False,
                conflict="crash",
            )

        assert db.session.query(educational_models.EducationalInstitution).count() == 0
        assert db.session.query(educational_models.EducationalDeposit).count() == 0
        assert str(exception.value) == "UAIs not found in adage: ['pouet']"

    def test_deposit_alread_in_ministry_replace(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        old_institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=old_institution,
            educationalYear=ansco,
            ministry=educational_models.Ministry.AGRICULTURE,
        )
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            final=False,
            conflict="replace",
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitution == institution,
                educational_models.EducationalDeposit.educationalYear == ansco,
            )
            .one()
        )

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

    def test_deposit_alread_in_ministry_keep(self) -> None:
        ansco = educational_factories.EducationalYearFactory()
        old_institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=old_institution,
            educationalYear=ansco,
            ministry=educational_models.Ministry.AGRICULTURE,
        )
        data = {"0470010E": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            final=False,
            conflict="keep",
        )

        institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId="0470010E").one()
        )
        deposit = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitution == institution,
                educational_models.EducationalDeposit.educationalYear == ansco,
            )
            .one()
        )

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
                    ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
                    final=False,
                    conflict="replace",
                    program_name=None,
                )

        institution = db.session.query(educational_models.EducationalInstitution).filter_by(institutionId=uai).one()
        new_institution = (
            db.session.query(educational_models.EducationalInstitution).filter_by(institutionId=new_uai).one()
        )
        deposit = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalYear == ansco,
                educational_models.EducationalDeposit.educationalInstitution == institution,
            )
            .one()
        )
        deposit_new_uai = (
            db.session.query(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalYear == ansco,
                educational_models.EducationalDeposit.educationalInstitution == new_institution,
            )
            .one()
        )

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

        assert deposit_new_uai.amount == Decimal(1500)
        assert deposit_new_uai.dateCreated - date_utils.get_naive_utc_now() < timedelta(seconds=5)
        assert deposit_new_uai.isFinal is False
        assert deposit_new_uai.ministry == educational_models.Ministry.EDUCATION_NATIONALE
