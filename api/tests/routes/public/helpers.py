import contextlib
import typing
import uuid

import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.models import db

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class PublicAPIEndpointBaseHelper:
    """
    For Public API endpoints that require authentication
    """

    @property
    def endpoint_url(self):
        raise NotImplementedError("You must add an attribute `endpoint_url` in your test class definition")

    @property
    def endpoint_method(self):
        """
        Http verb used to call the endpoint
        Expected values: 'get', 'post', 'patch', 'delete'
        """
        raise NotImplementedError("You must add an attribute `endpoint_method` in your test class definition")

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

    def test_should_raise_401_because_api_key_not_linked_to_provider(
        self, client: TestClient, num_queries: int | None = None
    ):
        """
        Default test ensuring the API call is authenticated and that the API key authenticates a provider
        """
        plain_api_key = self.setup_old_api_key()
        client_method = getattr(client.with_explicit_token(plain_api_key), self.endpoint_method)
        url = self.endpoint_url

        if self.default_path_params:
            url = url.format(**self.default_path_params)

        # TODO: (tcoudray-pass, 23/06/25) Restore `testing.assert_num_queries` when all public API endpoints use `@atomic`
        response = client_method(url)
        assert response.status_code == 401

        assert response.json == {"auth": "Deprecated API key. Please contact provider support to get a new API key"}

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

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        raise NotImplementedError()

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


class PublicAPIRestrictedEnvEndpointHelper(PublicAPIVenueEndpointHelper):
    @pytest.mark.settings(IS_PROD=True)
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

    def setup_method(self):
        self.plain_api_key, _ = self.setup_provider()

    def get_authenticated_client(self, client):
        if not hasattr(self, "_authenticated_client"):
            self._authenticated_client = client.with_explicit_token(self.plain_api_key)
        return self._authenticated_client

    def assert_request_has_expected_result(
        self, client, url_params: dict, expected_status_code: int, expected_error_json: dict | None = None
    ):
        # response = self.send_request(self.get_authenticated_client(client), url_params=url_params)
        response = self.send_request(client, url_params=url_params)
        assert response.status_code == expected_status_code, self._format_wrong_status_code(
            response, expected_status_code
        )
        if expected_error_json is not None:
            for key, msg in expected_error_json.items():
                assert response.json.get(key) == msg, f"[{key}] expected: {msg}, got: '{response.json.get(key)}'"
                assert response.json.get(key) == msg, self._format_unexpected_json_error(response, key, msg)

        return response

    def _format_wrong_status_code(self, response, expected_status):
        return f"expected: {expected_status}, got: {response.status_code}, json: '{response.json}'"

    def _format_unexpected_json_error(self, response, key, expected_value):
        return f"expected: '{key}: {expected_value}', got: '{key}: {response.json.get(key)}'"


class ProductEndpointHelper:
    @staticmethod
    def create_base_product(
        venue: offerers_models.Venue, provider: providers_models.Provider | None = None, **extra: typing.Any
    ) -> offers_models.Offer:
        base_kwargs = {
            "venue": venue,
            "lastProviderId": provider and provider.id,
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "description": "Un livre de contrepèterie",
            "name": "Vieux motard que jamais",
            "ean": "1234567890123",
        }

        return offers_factories.ThingOfferFactory(**{**base_kwargs, **extra})


@contextlib.contextmanager
def assert_attribute_value_changes_to(model, attribute_name, expected_value):
    previous_value = getattr(model, attribute_name)

    yield

    db.session.refresh(model)
    assert getattr(model, attribute_name) != previous_value
    assert getattr(model, attribute_name) == expected_value


@contextlib.contextmanager
def assert_attribute_does_not_change(model, attribute_name):
    previous_value = getattr(model, attribute_name)

    yield

    db.session.refresh(model)
    assert getattr(model, attribute_name) == previous_value
