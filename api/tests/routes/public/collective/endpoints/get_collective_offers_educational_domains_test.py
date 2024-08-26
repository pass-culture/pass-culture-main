from operator import itemgetter

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalDomainsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-domains"
    endpoint_method = "get"

    def test_list_educational_domains(self, client):
        # Given
        plain_api_key, _ = self.setup_provider()

        programs = educational_factories.NationalProgramFactory.create_batch(2)

        domain1 = educational_factories.EducationalDomainFactory(name="Arts numériques", nationalPrograms=programs)
        domain2 = educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel")

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        # Then
        assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        domain1_programs = [{"id": p.id, "name": p.name} for p in programs]
        assert response_list == [
            {"id": domain1.id, "name": "Arts numériques", "nationalPrograms": domain1_programs},
            {"id": domain2.id, "name": "Cinéma, audiovisuel", "nationalPrograms": []},
        ]

    def test_list_educational_domains_empty(self, client):
        # Given
        plain_api_key, _ = self.setup_provider()

        # When
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_list_educational_domains_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get(self.endpoint_url)

        # Then
        assert response.status_code == 401
