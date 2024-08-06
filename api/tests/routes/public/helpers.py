import abc
import uuid

import pytest

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

    @abc.abstractmethod
    def test_should_raise_401_because_not_authenticated(self, client: TestClient):
        raise NotImplementedError()

    def setup_provider(self) -> tuple[str, providers_models.Provider]:
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory(name="Technical provider")
        providers_factories.OffererProviderFactory(
            offerer=offerer,
            provider=provider,
        )

        secret = str(uuid.uuid4())
        env = "test"
        prefix_id = str(uuid.uuid1())

        offerers_factories.ApiKeyFactory(
            offerer=offerer, provider=provider, secret=secret, prefix="%s_%s" % (env, prefix_id)
        )
        plain_api_key = "%s_%s_%s" % (env, prefix_id, secret)

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

    def setup_inactive_venue_provider(self) -> tuple[str, providers_models.VenueProvider]:
        plain_api_key, provider = self.setup_provider()
        venue = self.setup_venue()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)

        return plain_api_key, venue_provider

    def setup_active_venue_provider(self) -> tuple[str, providers_models.VenueProvider]:
        plain_api_key, provider = self.setup_provider()
        venue = self.setup_venue()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

        return plain_api_key, venue_provider


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
