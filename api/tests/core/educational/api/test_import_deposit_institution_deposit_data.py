from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api.institution import import_deposit_institution_data


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

        institution = educational_models.EducationalInstitution.query.filter_by(institutionId="0470010E").one()
        deposit = educational_models.EducationalDeposit.query.filter(
            educational_models.EducationalDeposit.educationalInstitution == institution,
            educational_models.EducationalDeposit.educationalYear == ansco,
        ).one()

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive == True
        assert deposit.amount == Decimal(1250)
        assert deposit.dateCreated - datetime.utcnow() < timedelta(seconds=5)
        assert deposit.isFinal == False
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

        institution = educational_models.EducationalInstitution.query.filter_by(institutionId="0470010E").one()
        deposit = educational_models.EducationalDeposit.query.filter(
            educational_models.EducationalDeposit.educationalInstitution == institution,
            educational_models.EducationalDeposit.educationalYear == ansco,
        ).one()

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive == True
        assert deposit.amount == Decimal(1250)
        assert deposit.dateCreated - datetime.utcnow() < timedelta(seconds=5)
        assert deposit.isFinal == False
        assert deposit.ministry == educational_models.Ministry.EDUCATION_NATIONALE

    def test_institution_not_in_adage(self):
        ansco = educational_factories.EducationalYearFactory()
        data = {"pouet": 1250}

        import_deposit_institution_data(
            data=data,
            educational_year=ansco,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE,
            final=False,
            conflict="crash",
        )

        assert educational_models.EducationalInstitution.query.count() == 0
        assert educational_models.EducationalDeposit.query.count() == 0

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

        institution = educational_models.EducationalInstitution.query.filter_by(institutionId="0470010E").one()
        deposit = educational_models.EducationalDeposit.query.filter(
            educational_models.EducationalDeposit.educationalInstitution == institution,
            educational_models.EducationalDeposit.educationalYear == ansco,
        ).one()

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive == True
        assert deposit.amount == Decimal(1250)
        assert deposit.isFinal == False
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

        institution = educational_models.EducationalInstitution.query.filter_by(institutionId="0470010E").one()
        deposit = educational_models.EducationalDeposit.query.filter(
            educational_models.EducationalDeposit.educationalInstitution == institution,
            educational_models.EducationalDeposit.educationalYear == ansco,
        ).one()

        assert institution.institutionId == "0470010E"
        assert institution.institutionType == "COLLEGE"
        assert institution.name == "Balamb Garden"
        assert institution.city == "Balamb"
        assert institution.postalCode == "75001"
        assert institution.email == "contact+squall@example.com"
        assert institution.phoneNumber == "0600000000"
        assert institution.isActive == True
        assert deposit.amount == Decimal(1250)
        assert deposit.isFinal == False
        assert deposit.ministry == educational_models.Ministry.AGRICULTURE
