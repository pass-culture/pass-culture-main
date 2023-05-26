import pytest

import pcapi.core.educational.factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="redactor")
def redactor_fixture() -> educational_factories.EducationalRedactorFactory:
    return educational_factories.EducationalRedactorFactory()


@pytest.fixture(name="adage_client")
def adage_client_fixture(client, redactor) -> "TestClient":
    institution = educational_factories.EducationalInstitutionFactory()
    return client.with_adage_token(email=redactor.email, uai=institution.institutionId)


class GetCollectiveRequestTest:
    def test_get_collective_request(self, adage_client, redactor):
        request = educational_factories.CollectiveOfferRequestFactory(educationalRedactor=redactor)

        dst = f"/adage-iframe/collective/offers-template/request/{request.id}"
        response = adage_client.get(dst)

        assert response.status_code == 200

        data = response.json
        assert data["id"] == request.id
        assert data["comment"] == request.comment

    def test_unauthorized(self, adage_client):
        """
        Test that a redactor can only retrieve its own collective offer
        requests.
        """
        another_redactor = educational_factories.EducationalRedactorFactory()
        request = educational_factories.CollectiveOfferRequestFactory(educationalRedactor=another_redactor)

        dst = f"/adage-iframe/collective/offers-template/request/{request.id}"
        assert adage_client.get(dst).status_code == 403

    def test_not_found(self, adage_client):
        dst = "/adage-iframe/collective/offers-template/request/0"
        assert adage_client.get(dst).status_code == 404
