from datetime import datetime
from datetime import timedelta

from pcapi.models import LocalProviderEvent
from pcapi.models import Provider
from pcapi.models.local_provider_event import LocalProviderEventType


def find_latest_sync_part_end_event(provider: Provider) -> LocalProviderEvent:
    return (
        LocalProviderEvent.query.filter(
            (LocalProviderEvent.provider == provider)
            & (LocalProviderEvent.type == LocalProviderEventType.SyncPartEnd)
            & (LocalProviderEvent.date > datetime.utcnow() - timedelta(days=25))
        )
        .order_by(LocalProviderEvent.date.desc())
        .first()
    )
