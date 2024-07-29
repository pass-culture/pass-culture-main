import abc
import uuid

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models


pytestmark = pytest.mark.usefixtures("db_session")


class PublicAPIEndpointBaseHelper(abc.ABC):
    @property
    @abc.abstractmethod
    def endpoint_url(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def test_should_raise_401_because_not_authenticated(self, client):
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
    @abc.abstractmethod
    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        raise NotImplementedError()

    @abc.abstractmethod
    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
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


class PublicAPIVenueWithPermissionEndpointHelper(PublicAPIVenueEndpointHelper):
    @property
    @abc.abstractmethod
    def needed_permission(self) -> tuple[providers_models.ApiResourceEnum, providers_models.PermissionEnum]:
        raise NotImplementedError()

    @abc.abstractmethod
    def test_should_raise_403_because_missing_permission(self, client):
        raise NotImplementedError()

    def setup_active_venue_provider_with_permissions(self) -> tuple[str, providers_models.VenueProvider]:
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        resource, permission = self.needed_permission
        providers_factories.VenueProviderPermissionFactory(
            venueProvider=venue_provider, resource=resource, permission=permission
        )

        return plain_api_key, venue_provider
