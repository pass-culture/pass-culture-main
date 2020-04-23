from models.user_sql_entity import UserSQLEntity
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_existing_webapp_user():
    query = keep_only_webapp_users(UserSQLEntity.query)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
