from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_existing_webapp_user():
    query = keep_only_webapp_users(UserSQLEntity.query)
    user = query.first()

    return {
        "user": get_beneficiary_helper(user)
    }
