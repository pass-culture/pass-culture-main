from datetime import datetime, timedelta

from models import LocalProviderEvent
from models.activity import load_activity
from models.db import db
from models.local_provider_event import LocalProviderEventType


def find_by_id_and_table_name(object_id, table_name):
    Activity = load_activity()
    result = db.session.query(Activity.id, Activity.verb, Activity.issued_at, Activity.changed_data) \
        .filter(Activity.table_name == table_name,
                Activity.data['id'].astext.cast(db.Integer) == object_id) \
        .all()
    return result


def find_latest_sync_part_end_event(provider):
    return LocalProviderEvent \
        .query \
        .filter((LocalProviderEvent.provider == provider) &
                (LocalProviderEvent.type == LocalProviderEventType.SyncPartEnd) &
                (LocalProviderEvent.date > datetime.utcnow() - timedelta(days=25))) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()


def find_latest_sync_start_event(provider):
    return LocalProviderEvent \
        .query \
        .filter((LocalProviderEvent.provider == provider) &
                (LocalProviderEvent.type == LocalProviderEventType.SyncStart)) \
        .order_by(LocalProviderEvent.date.desc()) \
        .first()