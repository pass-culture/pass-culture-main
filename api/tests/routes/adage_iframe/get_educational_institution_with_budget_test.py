import datetime
from typing import Any

import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_get_institution_budget(self, client: Any):
        # Given
        year1 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2021, 1, 1))
        year2 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2022, 1, 1))
        year3 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2023, 1, 1))

        deposit1 = educational_factories.EducationalDepositFactory(educationalYear=year1, amount=1000)
        deposit2 = educational_factories.EducationalDepositFactory(educationalYear=year2, amount=2000)
        deposit3 = educational_factories.EducationalDepositFactory(educationalYear=year3, amount=3000)
        institution = educational_factories.EducationalInstitutionFactory(deposits=[deposit1, deposit2, deposit3])

        educational_redactor = educational_factories.EducationalRedactorFactory()

        # When
        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get("/adage-iframe/collective/institution")

        # Then
        assert response.status_code == 200
        assert response.json["id"] == institution.id
        assert response.json["name"] == institution.name
        assert response.json["institutionType"] == "COLLEGE"
        assert response.json["postalCode"] == "75000"
        assert response.json["city"] == "PARIS"
        assert response.json["phoneNumber"] == "0600000000"
        assert response.json["budget"] == 3000


class Returns404Test:
    def test_get_institution_budget_year_not_found(self, client: Any):
        # Given
        year1 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2021, 1, 1))
        year2 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2022, 1, 1))
        year3 = educational_factories.EducationalYearFactory(beginningDate=datetime.date(2020, 1, 1))

        deposit1 = educational_factories.EducationalDepositFactory(educationalYear=year1, amount=1000)
        deposit2 = educational_factories.EducationalDepositFactory(educationalYear=year2, amount=2000)
        deposit3 = educational_factories.EducationalDepositFactory(educationalYear=year3, amount=3000)
        institution = educational_factories.EducationalInstitutionFactory(deposits=[deposit1, deposit2, deposit3])

        educational_redactor = educational_factories.EducationalRedactorFactory()

        # When
        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get("/adage-iframe/collective/institution")

        # Then
        assert response.status_code == 404
        assert response.json == {"global": "L'établissement scolaire ne semble pas avoir de budget pour cette année."}

    def test_get_institution_budget_no_deposit(self, client: Any):
        # Given
        institution = educational_factories.EducationalInstitutionFactory(deposits=[])

        educational_redactor = educational_factories.EducationalRedactorFactory()

        # When
        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get("/adage-iframe/collective/institution")

        # Then
        assert response.status_code == 404
        assert response.json == {"global": "L'établissement scolaire ne semble pas exister."}
