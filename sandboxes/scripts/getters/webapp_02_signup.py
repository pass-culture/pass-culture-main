from models.user import User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_existing_webapp_user():
    query = filter_webapp_users(User.query)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
