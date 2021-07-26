from unittest.mock import call
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.local_providers.provider_api.provider_api_stocks import synchronize_stocks


class ProviderApiStocksTest:
    @patch("pcapi.local_providers.provider_api.synchronize_provider_api.synchronize_venue_provider")
    @pytest.mark.usefixtures("db_session")
    def test_synchronize_venue_providers(self, mocked_synchronize_venue_provider, app):
        # Given
        api_provider_1 = offerers_factories.APIProviderFactory()
        api_provider_2 = offerers_factories.APIProviderFactory()
        specific_provider = offerers_factories.AllocineProviderFactory()
        inactive_provider = offerers_factories.APIProviderFactory(isActive=False)

        correct_venue_providers = [
            VenueProviderFactory(isActive=True, provider=api_provider_1),
            VenueProviderFactory(isActive=True, provider=api_provider_1),
            VenueProviderFactory(isActive=True, provider=api_provider_2),
        ]

        VenueProviderFactory(isActive=True, provider=specific_provider)
        VenueProviderFactory(isActive=False, provider=api_provider_1)
        VenueProviderFactory(isActive=True, provider=inactive_provider)

        # When
        synchronize_stocks()

        # Then
        assert mocked_synchronize_venue_provider.call_count == len(correct_venue_providers)
        mocked_synchronize_venue_provider.assert_has_calls(call(v) for v in correct_venue_providers)
