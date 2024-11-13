import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/test-security", methods=["GET"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def security_endpoint(
    authenticated_information: AuthenticatedInformation,
) -> None:
    return


pytestmark = pytest.mark.usefixtures("db_session")


class AuthenticatedInformationTest:
    def test_authenticated_information_success(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        response = test_client.get("/adage-iframe/test-security")

        assert response.status_code == 204

    def test_authenticated_information_no_email(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(email=None, uai=educational_institution.institutionId)
        response = test_client.get("/adage-iframe/test-security")

        assert response.status_code == 401
        assert response.json == {"Authorization": "Unrecognized token"}
