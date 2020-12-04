from pcapi.models import UserSQLEntity
from pcapi.models import db


def get_base_query(min_id):
    return UserSQLEntity.query.filter(
        UserSQLEntity.isBeneficiary == False,
        UserSQLEntity.canBookFreeOffers == True,
        UserSQLEntity.isAdmin == False,
        UserSQLEntity.id > min_id,
    )


def get_ids_query(min_id):
    return get_base_query(min_id).order_by(UserSQLEntity.id).with_entities(UserSQLEntity.id)


def migrate_can_book_free_offer_data(batch_size=1000):
    item_count = get_ids_query(0).count()
    print(f"{item_count} users to update")
    if item_count == 0:
        return

    modified_sum = 0
    min_id = 0
    item_ids = get_ids_query(min_id).limit(batch_size).all()
    max_id = item_ids[-1][0]
    while item_ids:
        modified_count = get_base_query(min_id).filter(UserSQLEntity.id <= max_id).update({"isBeneficiary": True})
        db.session.commit()
        item_ids = get_ids_query(max_id).limit(batch_size).all()
        min_id, max_id = max_id, item_ids[-1][0]
        print(f"{modified_count} users modified out of {batch_size}")
        modified_sum += modified_count

    print(f"{modified_sum} users updated")
