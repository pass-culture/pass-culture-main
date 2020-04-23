from models.user_sql_entity import UserSQLEntity
from models.user_offerer import UserOfferer
from sandboxes.scripts.utils.helpers import get_user_helper, get_offerer_helper

def get_existing_pro_user_with_offerer():
    query = UserSQLEntity.query.join(UserOfferer)
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }


def get_existing_pro_not_validated_user_with_real_offerer():
    users = UserSQLEntity.query \
        .filter(UserSQLEntity.validationToken is not None) \
        .join(UserOfferer) \
        .all()

    for user in users:
        if len(user.UserOfferers) == 1:
            return {
                'user': get_user_helper(user)
            }
