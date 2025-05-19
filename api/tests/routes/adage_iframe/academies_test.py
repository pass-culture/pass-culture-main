import pytest
from flask import url_for

from pcapi.core.educational import academies
from pcapi.core.educational import factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetAcademiesTest:
    def test_get_academies(self, client):
        educational_institution = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory()

        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.get(url_for("adage_iframe.get_academies"))

        assert response.status_code == 200
        assert sorted(response.json) == sorted(academies.ACADEMIES.keys())
