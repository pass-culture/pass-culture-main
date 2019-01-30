from models.recommendation import Recommendation
from models.user import User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper


def get_existing_webapp_user_with_profile():
    query = filter_webapp_users(User.query)
    query = query.filter(User.resetPasswordToken == None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
