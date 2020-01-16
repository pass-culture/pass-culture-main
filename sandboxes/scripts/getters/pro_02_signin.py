from models.user import User
from models.user_offerer import UserOfferer
from sandboxes.scripts.utils.helpers import get_user_helper


def get_existing_pro_not_validated_user():
    query = User.query.join(UserOfferer)
    query = query.filter(User.validationToken != None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }

def get_existing_pro_validated_user():
    query = User.query.join(UserOfferer)
    query = query.filter(User.validationToken == None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
