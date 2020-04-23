from models.user_sql_entity import UserSQLEntity
from models.user_offerer import UserOfferer
from sandboxes.scripts.utils.helpers import get_user_helper


def get_existing_pro_not_validated_user():
    query = UserSQLEntity.query.join(UserOfferer)
    query = query.filter(UserSQLEntity.validationToken != None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }

def get_existing_pro_validated_user():
    query = UserSQLEntity.query.join(UserOfferer)
    query = query.filter(UserSQLEntity.validationToken == None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
