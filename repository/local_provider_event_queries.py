from datetime import datetime, timedelta

from sqlalchemy import or_

from models import LocalProviderEvent, Provider
from models.local_provider_event import LocalProviderEventType


def find_latest_sync_part_end_event(provider: Provider) -> LocalProviderEvent:
    return LocalProviderEvent \
        .query \
        .filter((LocalProviderEvent.provider == provider) &
                (LocalProviderEvent.type == LocalProviderEventType.SyncPartEnd) &
                (LocalProviderEvent.date > datetime.utcnow() - timedelta(days=25))) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()


def find_latest_sync_end_event(provider: Provider) -> LocalProviderEvent:
    return LocalProviderEvent \
        .query \
        .filter((LocalProviderEvent.provider == provider) &
                (LocalProviderEvent.type == LocalProviderEventType.SyncEnd)) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()


def find_latest_sync_start_event(provider: Provider) -> LocalProviderEvent:
    return LocalProviderEvent \
        .query \
        .filter((LocalProviderEvent.provider == provider) &
                (LocalProviderEvent.type == LocalProviderEventType.SyncStart)) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()


def find_lastest_sync_end_or_sync_part_end_for_provider(provider: Provider) -> LocalProviderEvent:
    return LocalProviderEvent.query \
        .filter(or_(LocalProviderEvent.type == LocalProviderEventType.SyncPartEnd,
                    LocalProviderEvent.type == LocalProviderEventType.SyncEnd)) \
        .filter(LocalProviderEvent.provider == provider) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()
