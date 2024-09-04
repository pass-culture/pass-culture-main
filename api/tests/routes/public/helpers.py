import abc
import uuid

import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class PublicAPIEndpointBaseHelper(abc.ABC):
    """
    For Public API endpoints that require authentication
    """

    @property
    @abc.abstractmethod
    def endpoint_url(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def endpoint_method(self):
        """
        Http verb used to call the endpoint
        Expected values: 'get', 'post', 'patch', 'delete'
        """
        raise NotImplementedError()

    @property
    def default_path_params(self) -> dict:
        """
        Default path params that will be used by default test to build an actual url.
        For instance, if `endpoint_url="/public/offers/v1/events/{event_id}"`, then
        `default_path_params` should look something like `{"event_id": 1}`
        """
        return {}

    def test_should_raise_401_because_not_authenticated(self, client: TestClient):
        """
        Default test ensuring the API call is authenticated before proceeding
        """
        client_method = getattr(client, self.endpoint_method)
        url = self.endpoint_url

        if self.default_path_params:
            url = url.format(**self.default_path_params)
        with testing.assert_num_queries(0):
            response = client_method(url)
            assert response.status_code == 401

        assert response.json == {"auth": "API key required"}

    def _setup_api_key(self, offerer, provider=None) -> str:
        secret = str(uuid.uuid4())
        env = "test"
        prefix_id = str(uuid.uuid1())

        offerers_factories.ApiKeyFactory(
            offerer=offerer, provider=provider, secret=secret, prefix="%s_%s" % (env, prefix_id)
        )
        plain_api_key = "%s_%s_%s" % (env, prefix_id, secret)

        return plain_api_key

    def setup_old_api_key(self) -> str:
        """
        Setup old api key not linked to a provider
        """
        offerer = offerers_factories.OffererFactory(name="Technical provider")
        return self._setup_api_key(offerer=offerer)

    def setup_provider(self, has_ticketing_urls=True) -> tuple[str, providers_models.Provider]:
        if has_ticketing_urls:
            provider = providers_factories.PublicApiProviderFactory()
        else:
            provider = providers_factories.ProviderFactory()
        offerer = offerers_factories.OffererFactory(name="Technical provider")
        providers_factories.OffererProviderFactory(
            offerer=offerer,
            provider=provider,
        )

        plain_api_key = self._setup_api_key(offerer=offerer, provider=provider)

        return plain_api_key, provider

    def setup_venue(self) -> offerers_models.Venue:
        return offerers_factories.VenueFactory()


class PublicAPIVenueEndpointHelper(PublicAPIEndpointBaseHelper):
    """
    For Public API endpoints that require an active `VenueProvider`
    """

    @abc.abstractmethod
    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        raise NotImplementedError()

    @abc.abstractmethod
    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        raise NotImplementedError()

    def setup_inactive_venue_provider(
        self, provider_has_ticketing_urls=True
    ) -> tuple[str, providers_models.VenueProvider]:
        plain_api_key, provider = self.setup_provider(provider_has_ticketing_urls)
        venue = self.setup_venue()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)

        return plain_api_key, venue_provider

    def setup_active_venue_provider(
        self, provider_has_ticketing_urls=True
    ) -> tuple[str, providers_models.VenueProvider]:
        plain_api_key, provider = self.setup_provider(provider_has_ticketing_urls)
        venue = self.setup_venue()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

        return plain_api_key, venue_provider


class PublicAPIRestrictedEnvEndpointHelper(PublicAPIEndpointBaseHelper):
    @testing.override_settings(IS_PROD=True)
    def test_should_not_be_usable_from_production_env(self, client):
        plain_api_key, _ = self.setup_provider()
        authenticated_client = client.with_explicit_token(plain_api_key)

        url = self.endpoint_url

        if self.default_path_params:
            url = url.format(**self.default_path_params)

        client_method = getattr(authenticated_client, self.endpoint_method)
        response = client_method(url)

        assert response.status_code == 403
        assert "unauthorized action" in response.json["msg"]

    def send_request(self, client, url_params=None, **kwargs):
        client_func = getattr(client, self.endpoint_method)
        url = self.endpoint_url

        if self.default_path_params or url_params:
            default = self.default_path_params if self.default_path_params else {}
            extra = url_params if url_params else {}
            params = {**default, **extra}
            url = url.format(**params)

        return client_func(url, **kwargs)


class ProductEndpointHelper:
    @staticmethod
    def create_base_product(
        venue: offerers_models.Venue, provider: providers_models.Provider | None = None
    ) -> offers_models.Offer:
        return offers_factories.ThingOfferFactory(
            venue=venue,
            lastProviderId=provider and provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
