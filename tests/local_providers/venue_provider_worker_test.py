from unittest import mock

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.models import VenueProvider
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.local_providers.venue_provider_worker import do_sync_venue_provider
from pcapi.local_providers.venue_provider_worker import update_venues_for_specific_provider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class UpdateVenuesForSpecificProviderTest:
    @override_features(PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER=False)
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

    @override_features(PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER=True)
    @override_settings(PROVIDERS_SYNC_WORKERS_POOL_SIZE=1)
    @mock.patch("pcapi.local_providers.venue_provider_worker.sleep")
    @mock.patch("pcapi.local_providers.venue_provider_worker.do_sync_venue_provider")
    @mock.patch("pcapi.local_providers.venue_provider_worker.get_nb_containers_at_work")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_sync_venue_provider_until_reaching_max_pool_size(
        self, mock_get_nb_containers_at_work, mock_do_sync_venue_provider, mock_sleep, app
    ):
        # Given
        mock_get_nb_containers_at_work.side_effect = [0, 1, 0]
        titelive_provider = activate_provider("TiteLiveStocks")
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue2 = create_venue(offerer, siret="12345678912356")
        venue_provider_titelive1 = create_venue_provider(venue1, titelive_provider)
        venue_provider_titelive2 = create_venue_provider(venue2, titelive_provider)
        repository.save(venue_provider_titelive1, venue_provider_titelive2)
        expected_wait_time = 60

        # When
        update_venues_for_specific_provider(titelive_provider.id)

        # Then
        mock_sleep.assert_called_once_with(expected_wait_time)
        assert mock_get_nb_containers_at_work.call_count == 3
        assert mock_do_sync_venue_provider.call_count == 2
        assert mock.call(venue_provider_titelive1) in mock_do_sync_venue_provider.call_args_list
        assert mock.call(venue_provider_titelive2) in mock_do_sync_venue_provider.call_args_list


@pytest.mark.usefixtures("db_session")
class DoSyncVenueProviderTest:
    @mock.patch("pcapi.local_providers.venue_provider_worker.run_process_in_one_off_container")
    def test_should_call_run_process_in_one_off_container_function(self, mock_run_process_in_one_off_container, app):
        # Given
        mock_run_process_in_one_off_container.return_value = "azertyTE7898RTYUIZERTYUI"
        titelive_provider = activate_provider("TiteLiveStocks")
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue_provider = create_venue_provider(venue1, titelive_provider)
        repository.save(venue_provider)
        update_venue_provider_command = (
            f"python src/pcapi/scripts/pc.py update_providables" f" --venue-provider-id {venue_provider.id}"
        )

        # When
        do_sync_venue_provider(venue_provider)

        # Then
        mock_run_process_in_one_off_container.assert_called_once_with(update_venue_provider_command)

    @mock.patch("pcapi.local_providers.venue_provider_worker.run_process_in_one_off_container")
    def test_should_update_venue_provider_with_worker_id(self, mock_run_process_in_one_off_container, app):
        # Given
        mock_run_process_in_one_off_container.return_value = "azertyTE7898RTYUIZERTYUI"
        titelive_provider = activate_provider("TiteLiveStocks")
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue_provider = create_venue_provider(venue1, titelive_provider, venue_id_at_offer_provider="12345")
        repository.save(venue_provider)

        # When
        do_sync_venue_provider(venue_provider)

        # Then
        updated_venue_provider = VenueProvider.query.one()
        assert updated_venue_provider.syncWorkerId == "azertyTE7898RTYUIZERTYUI"
