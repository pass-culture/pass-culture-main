from models.activity import load_activity
from models.db import db


def find_by_id_and_table_name(object_id, table_name):
    Activity = load_activity()
    result = db.session.query(Activity.id, Activity.verb, Activity.issued_at, Activity.changed_data) \
        .filter(Activity.table_name == table_name,
                Activity.data['id'].astext.cast(db.Integer) == object_id) \
        .all()
    return result