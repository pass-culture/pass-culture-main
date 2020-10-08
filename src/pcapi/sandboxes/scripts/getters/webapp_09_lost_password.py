from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper

def get_webapp_user_with_not_validated_password():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.resetPasswordToken != None)
    user = query.first()

    return {
        "user": get_beneficiary_helper(user)
    }
