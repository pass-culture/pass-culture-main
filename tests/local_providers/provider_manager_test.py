from unittest.mock import MagicMock, patch, ANY

from local_providers.provider_manager import do_update, _remove_worker_id_after_venue_provider_sync_error
from models import VenueProvider, PcObject
from tests.conftest import clean_database
from tests.local_providers.provider_test_utils import TestLocalProvider
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer, create_provider


def mock_update_objects():
    raise Exception


class DoUpdateTest:
    def test_should_call_provider_updateObjects_function(self, app):
        # Given
        provider_mock = MagicMock()
        provider_mock.updateObjects = MagicMock()

        # When
        do_update(provider_mock, 10)

        # Then
        provider_mock.updateObjects.assert_called_once_with(10)

    @patch('local_providers.provider_manager.build_cron_log_message')
    @patch('local_providers.provider_manager._remove_worker_id_after_venue_provider_sync_error')
    def test_should_call_remove_worker_id_when_exception_is_raised(self, mock_remove_worker_id,
                                                                   mock_build_cron_log_message,
                                                                   app):
        # Given
        provider_mock = MagicMock()
        provider_mock.updateObjects = mock_update_objects

        # When
        do_update(provider_mock, 10)

        # Then
        mock_remove_worker_id.assert_called_once_with(provider_mock)
        mock_build_cron_log_message.assert_called_once_with(name='MagicMock',
                                                            status=ANY,
                                                            traceback=ANY)


class RemoveWorkerIdAfterVenueProviderSyncErrorTest:
    @clean_database
    def test_should_not_update_model_when_no_venue_provider_attached_to_provider(self, app):
        # Given
        provider = TestLocalProvider()

        # When
        _remove_worker_id_after_venue_provider_sync_error(provider)

        # Then
        assert VenueProvider.query.count() == 0

    @clean_database
    def test_should_remove_worker_id_value(self, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        PcObject.save(provider_test)
        offerer = create_offerer()
        venue_1 = create_venue(offerer, siret='12345678901234')
        venue_provider = create_venue_provider(venue_1, provider_test, sync_worker_id='1234567')
        PcObject.save(venue_provider)

        provider = TestLocalProvider(venue_provider)

        # When
        _remove_worker_id_after_venue_provider_sync_error(provider)

        # Then
        updated_venue_provider = VenueProvider.query.one()
        assert updated_venue_provider.syncWorkerId is None
