from operator import itemgetter

import pytest

import pcapi.core.educational.factories as educational_factories
from pcapi.core import testing

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalDomainsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/educational-domains"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select educational_domain

    def test_list_educational_domains(self):
        plain_api_key, _ = self.setup_provider()

        active_programs = educational_factories.NationalProgramFactory.create_batch(2)
        programs = [
            *active_programs,
            # this inactive program will not appear in the response
            educational_factories.NationalProgramFactory(isActive=False),
        ]

        domain1 = educational_factories.EducationalDomainFactory(name="Arts numériques", nationalPrograms=programs)
        domain2 = educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel")

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        domain1_programs = [{"id": p.id, "name": p.name} for p in active_programs]
        assert response_list == [
            {"id": domain1.id, "name": "Arts numériques", "nationalPrograms": domain1_programs},
            {"id": domain2.id, "name": "Cinéma, audiovisuel", "nationalPrograms": []},
        ]

    def test_list_educational_domains_empty(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert response.json == []
