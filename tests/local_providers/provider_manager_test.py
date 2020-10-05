from unittest.mock import MagicMock, patch, ANY

from local_providers.provider_manager import do_update, _remove_worker_id_after_venue_provider_sync_error, \
    synchronize_venue_provider, synchronize_venue_providers_for_provider, synchronize_data_for_provider
from models import VenueProvider
from repository import repository
import pytest
from tests.local_providers.provider_test_utils import TestLocalProvider
from tests.model_creators.generic_creators import create_allocine_venue_provider
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer, create_provider
from tests.model_creators.provider_creators import activate_provider
from tests.test_utils import fake


def mock_update_objects():
    raise Exception


def mock_init_provider(*arg):
    raise Exception


class DoUpdateTest:
    def test_should_call_provider_objects_synchronization_function(self, app):
        # Given
        provider_mock = MagicMock()
        provider_mock.updateObjects = MagicMock()

        # When
        do_update(provider_mock, 10)

        # Then
        provider_mock.updateObjects.assert_called_once_with(10)

    @patch('local_providers.provider_manager.build_cron_log_message')
    @patch('local_providers.provider_manager._remove_worker_id_after_venue_provider_sync_error')
    def test_should_call_remove_worker_id_when_exception_is_raised(self,
                                                                   mock_remove_worker_id,
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
    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_model_when_no_venue_provider_attached_to_provider(self, app):
        # Given
        provider = TestLocalProvider()

        # When
        _remove_worker_id_after_venue_provider_sync_error(provider)

        # Then
        assert VenueProvider.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_remove_worker_id_value(self, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(
            venue, provider_test, sync_worker_id='1234567')
        repository.save(venue_provider)

        provider = TestLocalProvider(venue_provider)

        # When
        _remove_worker_id_after_venue_provider_sync_error(provider)

        # Then
        updated_venue_provider = VenueProvider.query.one()
        assert updated_venue_provider.syncWorkerId is None


class SynchronizeVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @patch('local_providers.provider_manager.do_update')
    def test_should_start_synchronization_with_linked_provider(self, mock_do_update, mock_get_provider_class, app):
        # Given
        limit = 10
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = create_provider(local_class='TestLocalProvider')
        venue_provider = create_venue_provider(venue, provider)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_provider(venue_provider, limit)

        # Then
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), limit)

    @pytest.mark.usefixtures("db_session")
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @patch('local_providers.provider_manager.do_update')
    def test_should_init_provider_with_expected_venue_provider(self, mock_do_update, mock_get_provider_class, app):
        # Given
        limit = 10
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = create_provider(local_class='TestLocalProvider')
        venue_provider = create_venue_provider(venue, provider)
        repository.save(venue_provider)
        mock_provider_class = MagicMock()
        mock_get_provider_class.return_value = mock_provider_class

        # When
        synchronize_venue_provider(venue_provider, limit)

        # Then
        mock_provider_class.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @patch('local_providers.provider_manager.do_update')
    def test_should_init_allocine_stocks_provider_with_expected_allocine_venue_provider(self, mock_do_update,
                                                                                        mock_get_provider_class, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)

        provider = activate_provider('AllocineStocks')
        allocine_venue_provider = create_allocine_venue_provider(venue, provider, is_duo=True)
        repository.save(allocine_venue_provider)

        mock_provider_class = MagicMock()
        mock_get_provider_class.return_value = mock_provider_class

        # When
        synchronize_venue_provider(allocine_venue_provider, None)

        # Then
        mock_provider_class.assert_called_once()
        venue_provider_mock_arg = mock_provider_class.call_args[0][0]
        assert venue_provider_mock_arg == allocine_venue_provider
        assert venue_provider_mock_arg.isDuo

    @pytest.mark.usefixtures("db_session")
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @patch('local_providers.provider_manager.build_cron_log_message')
    def test_should_log_exception_when_one_is_raised_during_provider_initilization(self,
                                                                                   mock_build_cron_log_message,
                                                                                   mock_get_provider_class,
                                                                                   app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)

        mock_get_provider_class.return_value = mock_init_provider

        # When
        synchronize_venue_provider(venue_provider, 10)

        # Then
        mock_build_cron_log_message.assert_called_once_with(name='mock_init_provider',
                                                            status=ANY,
                                                            traceback=ANY)


class SynchronizeVenueProvidersForProviderTest:
    @patch('local_providers.provider_manager.do_update')
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @pytest.mark.usefixtures("db_session")
    def test_should_entirely_synchronize_venue_provider(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(provider_test.id, None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), None)

    @patch('local_providers.provider_manager.do_update')
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @pytest.mark.usefixtures("db_session")
    def test_should_synchronize_venue_provider_with_defined_limit(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(provider_test.id, 10)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), 10)

    @patch('local_providers.provider_manager.synchronize_venue_provider')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_synchronize_venue_provider(self, mock_synchronize_venue_provider, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)

        # When
        synchronize_venue_providers_for_provider(provider_test.id, 10)

        # Then
        mock_synchronize_venue_provider.assert_called_once()


class SynchronizeDataForProviderTest:
    @patch('local_providers.provider_manager.do_update')
    @patch('local_providers.provider_manager.get_local_provider_class_by_name')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_do_update_for_specified_provider(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = create_provider(local_class='TestLocalProvider')
        repository.save(provider_test)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_data_for_provider(provider_test.__class__.__name__, None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), None)
