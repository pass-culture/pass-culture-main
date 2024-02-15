from unittest.mock import patch

import pytest

from pcapi.core import testing
from pcapi.core.providers import commands
from pcapi.core.providers import factories


pytestmark = pytest.mark.usefixtures("db_session")


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

        queries = 1  # select providers and their venue providers
        # 1 select for each VenueProvider of not_parallel_provider,
        # in `synchronize_venue_providers_task()`
        queries += 2
        # 1 select for all VenueProvider of parallel_provider,
        # in `synchronize_venue_providers_task()`
        queries += 1
        with testing.assert_num_queries(queries):
            commands._synchronize_venue_providers_apis()

        assert len(mock_synchronize_venue_providers.call_args_list) == 3

        assert mock_synchronize_venue_providers.call_args_list[0][0][0] == [
            not_parallel_venue_provider_1,
            not_parallel_venue_provider_2,
        ]
        assert mock_synchronize_venue_providers.call_args_list[1][0][0] == [parallel_venue_provider_1]
        assert mock_synchronize_venue_providers.call_args_list[2][0][0] == [parallel_venue_provider_2]
