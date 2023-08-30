from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.providers import commands
from pcapi.core.providers import factories


class SynchronizeVenueProvidersApisTest:
    @patch("pcapi.local_providers.provider_manager.synchronize_venue_providers")
    def test_synchronize_venue_providers_apis(self, mock_synchronize_venue_providers):
        factories.ProviderFactory()

        not_parallel_provider = factories.APIProviderFactory()
        parallel_provider = factories.APIProviderFactory(enableParallelSynchronization=True)

        not_parallel_venue_provider_1 = factories.VenueProviderFactory(provider=not_parallel_provider)
        not_parallel_venue_provider_2 = factories.VenueProviderFactory(provider=not_parallel_provider)

        parallel_venue_provider_1 = factories.VenueProviderFactory(provider=parallel_provider)
        parallel_venue_provider_2 = factories.VenueProviderFactory(provider=parallel_provider)

        with testing.assert_num_queries(6):
            # FIXME(viconnex): there is N+1 queries because we don't use joinedload
            commands._synchronize_venue_providers_apis()

        assert len(mock_synchronize_venue_providers.call_args_list) == 3

        assert mock_synchronize_venue_providers.call_args_list[0][0][0] == [
            not_parallel_venue_provider_1,
            not_parallel_venue_provider_2,
        ]
        assert mock_synchronize_venue_providers.call_args_list[1][0][0] == [parallel_venue_provider_1]
        assert mock_synchronize_venue_providers.call_args_list[2][0][0] == [parallel_venue_provider_2]
