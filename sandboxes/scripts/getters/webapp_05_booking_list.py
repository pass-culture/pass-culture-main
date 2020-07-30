from models.user_sql_entity import UserSQLEntity
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_existing_webapp_user_with_bookings():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }
