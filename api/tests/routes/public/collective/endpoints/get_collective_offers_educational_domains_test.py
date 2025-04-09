from operator import itemgetter

import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as educational_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalDomainsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-domains"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select educational_domain

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_list_educational_domains(self, client):
        plain_api_key, _ = self.setup_provider()

        programs = educational_factories.NationalProgramFactory.create_batch(2)

        domain1 = educational_factories.EducationalDomainFactory(name="Arts numériques", nationalPrograms=programs)
        domain2 = educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel")

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        domain1_programs = [{"id": p.id, "name": p.name} for p in programs]
        assert response_list == [
            {"id": domain1.id, "name": "Arts numériques", "nationalPrograms": domain1_programs},
            {"id": domain2.id, "name": "Cinéma, audiovisuel", "nationalPrograms": []},
        ]

    def test_list_educational_domains_empty(self, client):
        plain_api_key, _ = self.setup_provider()

        client = client.with_explicit_token(plain_api_key)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(self.endpoint_url)
            assert response.status_code == 200

        assert response.json == []
