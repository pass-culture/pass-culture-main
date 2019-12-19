from datetime import datetime

from models import LocalProviderEvent, PcObject
from models.local_provider_event import LocalProviderEventType
from repository.local_provider_event_queries import find_latest_sync_end_event
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_provider


class FindLatestSyncEndEventTest:
    def test_return_none_when_no_event_happended(self, app):
        # Given
        provider = create_provider('Provider Test')
        PcObject.save(provider)

        # When
        last_event = find_latest_sync_end_event(provider)

        # Then
        assert last_event is None

    @clean_database
    def test_return_last_sync_event_from_the_provider(self, app):
        # Given
        provider = create_provider('Provider Test')

        most_recent_event = LocalProviderEvent()
        most_recent_event.provider = provider
        most_recent_event.type = LocalProviderEventType.SyncEnd
        most_recent_event.date = datetime(2000, 2, 2)

        older_event = LocalProviderEvent()
        older_event.provider = provider
        older_event.type = LocalProviderEventType.SyncEnd
        older_event.date = datetime(1900, 1, 1)

        PcObject.save(older_event, most_recent_event)

        # When
        last_event = find_latest_sync_end_event(provider)

        # Then
        assert last_event == most_recent_event
