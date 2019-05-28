from datetime import datetime

import pytest

from models import Provider, LocalProviderEvent, PcObject
from models.local_provider_event import LocalProviderEventType
from repository.local_provider_event_queries import find_latest_sync_end_event
from tests.conftest import clean_database


@pytest.mark.standalone
class FindLatestSyncEndEventTest:

    def test_return_none_when_no_event_happended(self, app):
        # Given
        provider = Provider()

        # When
        last_event = find_latest_sync_end_event(provider)

        # Then
        assert last_event == None

    @clean_database
    def test_return_last_sync_event_to_get_the(self, app):
        # Given
        provider = Provider.query.first()

        most_recent_event = LocalProviderEvent()
        most_recent_event.provider = provider
        most_recent_event.type = LocalProviderEventType.SyncEnd
        most_recent_event.date = datetime(2000, 2, 2)

        older_event = LocalProviderEvent()
        older_event.provider = provider
        older_event.type = LocalProviderEventType.SyncEnd
        older_event.date = datetime(1900, 1, 1)

        PcObject.check_and_save(older_event, most_recent_event)

        # When
        last_event = find_latest_sync_end_event(provider)

        # Then
        assert last_event == most_recent_event
