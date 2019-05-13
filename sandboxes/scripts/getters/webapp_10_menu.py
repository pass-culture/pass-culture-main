from models.user import User
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_existing_webapp_validated_user():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.resetPasswordToken == None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
