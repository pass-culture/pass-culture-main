import pytest
from flask import url_for

from pcapi.core.educational import factories as educational_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class SaveRedactorPreferencesTest:
    endpoint = "adage_iframe.save_redactor_preferences"

    def test_save_preferences(self, client, caplog):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()

        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.post(
            url_for(self.endpoint), json={"feedback_form_closed": True, "broadcast_help_closed": True}
        )

        assert response.status_code == 204

        db.session.refresh(educational_redactor)
        assert educational_redactor.preferences == {"feedback_form_closed": True, "broadcast_help_closed": True}
