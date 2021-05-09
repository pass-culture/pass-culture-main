from unittest import mock

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.local_providers.venue_provider_worker import update_venues_for_specific_provider


@pytest.mark.usefixtures("db_session")
class UpdateVenuesForSpecificProviderTest:
    @mock.patch("pcapi.local_providers.venue_provider_worker.synchronize_venue_provider")
    def test_should_call_sync_venue_provider_for_expected_venue_provider(self, mock_synchronize_venue_provider):
        # Given
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
        vp1 = offerers_factories.VenueProviderFactory(provider=provider)
        vp2 = offerers_factories.VenueProviderFactory(provider=provider)
        offerers_factories.VenueProviderFactory(provider=provider, isActive=False)
        other_provider = offerers_factories.ProviderFactory()
        offerers_factories.VenueProviderFactory(provider=other_provider)

        # When
        update_venues_for_specific_provider(provider.id)

        # Then
        assert mock_synchronize_venue_provider.call_args_list == [
            mock.call(vp1),
            mock.call(vp2),
        ]
