from flask import url_for
import pytest

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetProvidersPageTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.providers.get_providers"
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch providers and associated api keys (1 query)
    expected_num_queries = 3

    def test_get_providers(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Individual Offer API consumer")
        provider = providers_factories.ProviderFactory(name=offerer.name)
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(offerer=offerer, provider=provider)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        provider_rows = html_parser.extract_table_rows(response.data)

        provider_row = next((row for row in provider_rows if row["ID"] == str(provider.id)))
        assert provider_row["Prestataire technique"] == provider.name
        assert provider_row["SIREN"] == offerer.siren
        assert provider_row["Ville"] == offerer.city
        assert provider_row["Code postal"] == offerer.postalCode
        assert provider_row["URL du logo"] == ""
        assert provider_row["Nombre de clés d'API"] == str(1)
        assert provider_row["Actif pour les pros"] == "Oui"
        assert provider_row["Actif"] == "Oui"
