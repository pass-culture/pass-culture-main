import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest

import pcapi.core.providers.factories as providers_factories
from pcapi.local_providers.provider_api.provider_api_stocks import synchronize_stocks


class ProviderApiStocksTest:
    @patch("pcapi.local_providers.provider_api.synchronize_provider_api.synchronize_venue_provider")
    @pytest.mark.usefixtures("db_session")
    def test_synchronize_venue_providers(self, mocked_synchronize_venue_provider, app):
        # Given
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        api_provider_1 = providers_factories.APIProviderFactory()
        api_provider_2 = providers_factories.APIProviderFactory()
        specific_provider = providers_factories.AllocineProviderFactory()
        inactive_provider = providers_factories.APIProviderFactory(isActive=False)

        correct_venue_providers = [
            providers_factories.VenueProviderFactory(isActive=True, provider=api_provider_2, lastSyncDate=yesterday),
            providers_factories.VenueProviderFactory(isActive=True, provider=api_provider_1, lastSyncDate=two_days_ago),
            providers_factories.VenueProviderFactory(isActive=True, provider=api_provider_1, lastSyncDate=None),
        ]

        providers_factories.VenueProviderFactory(isActive=True, provider=specific_provider)
        providers_factories.VenueProviderFactory(isActive=False, provider=api_provider_1)
        providers_factories.VenueProviderFactory(isActive=True, provider=inactive_provider)

        # When
        synchronize_stocks()

        # Then
        assert mocked_synchronize_venue_provider.call_count == len(correct_venue_providers)
        mocked_synchronize_venue_provider.assert_has_calls(call(v) for v in reversed(correct_venue_providers))
