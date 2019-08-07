from models.user import User
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_webapp_user_with_not_validated_password():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.resetPasswordToken != None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
