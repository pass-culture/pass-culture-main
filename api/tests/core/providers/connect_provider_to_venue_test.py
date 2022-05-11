from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.api import connect_venue_to_provider
from pcapi.core.providers.exceptions import NoSiretSpecified
from pcapi.core.providers.exceptions import ProviderWithoutApiImplementation
from pcapi.core.providers.exceptions import VenueSiretNotRegistered
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import VenueProvider


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.infrastructure.repository.stock_provider.provider_api.ProviderAPI.is_siret_registered",
    return_value=True,
)
def test_when_venue_id_at_offer_provider_is_given(can_be_synchronized):
    # Given
    venue_id_at_offer_provider = "id_for_remote_system"
    venue = offerers_factories.VenueFactory(siret="12345678912345")
    provider = providers_factories.APIProviderFactory()

    # When
    connect_venue_to_provider(venue, provider, venue_id_at_offer_provider)

    # Then
    venue_provider = VenueProvider.query.one()
    assert venue_provider.venueIdAtOfferProvider == venue_id_at_offer_provider
    can_be_synchronized.assert_called_once_with("id_for_remote_system")


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.infrastructure.repository.stock_provider.provider_api.ProviderAPI.is_siret_registered",
    return_value=True,
)
def test_use_siret_as_default(can_be_synchronized):
    # Given
    venue = offerers_factories.VenueFactory(siret="12345678912345")
    provider = providers_factories.APIProviderFactory()

    # When
    connect_venue_to_provider(venue, provider, None)

    # Then
    venue_provider = VenueProvider.query.one()
    assert venue_provider.venueIdAtOfferProvider == "12345678912345"
    can_be_synchronized.assert_called_once_with("12345678912345")


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.providers.api._siret_can_be_synchronized", return_value=False)
def test_cannot_connect_when_synchronization_is_not_allowed(can_be_synchronized):
    venue = offerers_factories.VenueFactory()
    provider = providers_factories.APIProviderFactory()

    with pytest.raises(VenueSiretNotRegistered):
        connect_venue_to_provider(venue, provider)

    assert not VenueProvider.query.count()


@pytest.mark.usefixtures("db_session")
def test_cannot_connect_venue_when_venue_has_no_siret():
    venue = offerers_factories.VenueFactory(siret=None, comment="no siret")
    provider = providers_factories.APIProviderFactory()

    with pytest.raises(NoSiretSpecified):
        connect_venue_to_provider(venue, provider)

    assert not VenueProvider.query.count()


@pytest.mark.usefixtures("db_session")
def test_cannot_connect_if_provider_has_local_class():
    provider = providers_factories.ProviderFactory(apiUrl=None, localClass="Dummy")
    venue = offerers_factories.VenueFactory()

    with pytest.raises(ProviderWithoutApiImplementation):
        connect_venue_to_provider(venue, provider)

    assert not VenueProvider.query.count()
