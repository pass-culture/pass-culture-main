import re

from flask import url_for
import pytest

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models.validation_status_mixin import ValidationStatus

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


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


class CreateProviderTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.providers.create_provider"
    needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_create_provider(self, authenticated_client):
        form_data = {
            "name": "Individual Offer API consumer",
            "city": "Paris",
            "postal_code": "75008",
            "siren": "123456789",
            "logo_url": "https://example.org/image.png",
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data)
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])

        created_provider_alert = html_parser.extract_alert(redirected_response.data)
        assert re.search(
            rf"development{offerers_api.API_KEY_SEPARATOR}\w{{77}}", created_provider_alert
        ), "clear api key secret not found"

        created_provider = providers_models.Provider.query.order_by(providers_models.Provider.id.desc()).first()
        assert created_provider.name == form_data["name"]
        assert created_provider.logoUrl == form_data["logo_url"]
        assert created_provider.enabledForPro == form_data["enabled_for_pro"]
        assert created_provider.isActive == form_data["is_active"]

        assert created_provider.offererProvider is not None
        created_offerer = created_provider.offererProvider.offerer
        assert created_offerer.name == form_data["name"]
        assert created_offerer.city == form_data["city"]
        assert created_offerer.postalCode == form_data["postal_code"]
        assert created_offerer.siren == form_data["siren"]
        assert created_offerer.validationStatus == ValidationStatus.VALIDATED

        created_api_key = created_provider.apiKeys[0]
        assert created_api_key.offerer == created_offerer
