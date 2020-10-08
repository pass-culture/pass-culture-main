from unittest.mock import patch, call

from local_providers.venue_provider_worker import update_venues_for_specific_provider, do_sync_venue_provider
from models import VenueProvider
from repository import repository
import pytest
from model_creators.generic_creators import create_offerer, create_venue, create_venue_provider
from model_creators.provider_creators import activate_provider


class UpdateVenuesForSpecificProviderTest:
    @patch('local_providers.venue_provider_worker.do_sync_venue_provider')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_sync_venue_provider_for_expected_venue_provider(self,
                                                                         mock_do_sync_venue_provider,
                                                                         app):
        # Given
        titelive_provider = activate_provider('TiteLiveStocks')
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue2 = create_venue(offerer, siret='12345678912356')
        venue_provider_titelive1 = create_venue_provider(venue1, titelive_provider)
        venue_provider_titelive2 = create_venue_provider(venue2, titelive_provider)
        repository.save(venue_provider_titelive1, venue_provider_titelive2)

        # When
        update_venues_for_specific_provider(titelive_provider.id)

        # Then
        assert mock_do_sync_venue_provider.call_count == 2
        assert call(venue_provider_titelive1) in mock_do_sync_venue_provider.call_args_list
        assert call(venue_provider_titelive2) in mock_do_sync_venue_provider.call_args_list

    @patch.dict('os.environ', {"SYNC_WORKERS_POOL_SIZE": '1'})
    @patch('local_providers.venue_provider_worker.sleep')
    @patch('local_providers.venue_provider_worker.do_sync_venue_provider')
    @patch('local_providers.venue_provider_worker.get_nb_containers_at_work')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_sync_venue_provider_until_reaching_max_pool_size(self,
                                                                          mock_get_nb_containers_at_work,
                                                                          mock_do_sync_venue_provider,
                                                                          mock_sleep,
                                                                          app):
        # Given
        mock_get_nb_containers_at_work.side_effect = [0, 1, 0]
        titelive_provider = activate_provider('TiteLiveStocks')
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue2 = create_venue(offerer, siret='12345678912356')
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
        assert call(venue_provider_titelive1) in mock_do_sync_venue_provider.call_args_list
        assert call(venue_provider_titelive2) in mock_do_sync_venue_provider.call_args_list


class DoSyncVenueProviderTest:
    @patch('local_providers.venue_provider_worker.run_process_in_one_off_container')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_run_process_in_one_off_container_function(self,
                                                                   mock_run_process_in_one_off_container, app):
        # Given
        mock_run_process_in_one_off_container.return_value = 'azertyTE7898RTYUIZERTYUI'
        titelive_provider = activate_provider('TiteLiveStocks')
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue_provider = create_venue_provider(venue1, titelive_provider)
        repository.save(venue_provider)
        update_venue_provider_command = f"PYTHONPATH=. python scripts/pc.py update_providables" \
                                        f" --venue-provider-id {venue_provider.id}"

        # When
        do_sync_venue_provider(venue_provider)

        # Then
        mock_run_process_in_one_off_container.assert_called_once_with(update_venue_provider_command)

    @patch('local_providers.venue_provider_worker.run_process_in_one_off_container')
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue_provider_with_worker_id(self,
                                                         mock_run_process_in_one_off_container, app):
        # Given
        mock_run_process_in_one_off_container.return_value = 'azertyTE7898RTYUIZERTYUI'
        titelive_provider = activate_provider('TiteLiveStocks')
        offerer = create_offerer()
        venue1 = create_venue(offerer)
        venue_provider = create_venue_provider(venue1, titelive_provider, venue_id_at_offer_provider='12345')
        repository.save(venue_provider)

        # When
        do_sync_venue_provider(venue_provider)

        # Then
        updated_venue_provider = VenueProvider.query.one()
        assert updated_venue_provider.syncWorkerId == 'azertyTE7898RTYUIZERTYUI'
