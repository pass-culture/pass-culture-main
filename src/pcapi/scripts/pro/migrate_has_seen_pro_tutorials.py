from datetime import datetime

from pcapi.core.users.models import User
from pcapi.models import db


today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def get_base_query(min_id):
    return User.query.filter(
        User.is_beneficiary == False,
        User.hasSeenProTutorials == False,
        User.dateCreated < today,
        User.id > min_id,
    )


def get_ids_query(min_id):
    return get_base_query(min_id).order_by(User.id).with_entities(User.id)


def migrate_has_seen_pro_tutorials(batch_size=1000):
    item_count = get_ids_query(0).count()
    print(f"{item_count} users to update")
    if item_count == 0:
        return

    modified_sum = 0
    min_id = 0
    item_ids = get_ids_query(min_id).limit(batch_size).all()
    max_id = item_ids[-1][0]
    while item_ids:
        modified_count = (
            get_base_query(min_id)
            .filter(User.id <= max_id)
            .update({"hasSeenProTutorials": True}, synchronize_session=False)
        )
        db.session.commit()
        modified_sum += modified_count
        print(f"{modified_count} users modified out of {batch_size}")
        item_ids = get_ids_query(max_id).limit(batch_size).all()
        if item_ids:
            min_id, max_id = max_id, item_ids[-1][0]
    print(f"{modified_sum} users updated")
