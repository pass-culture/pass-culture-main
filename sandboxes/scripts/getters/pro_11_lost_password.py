from models.user import User
from sandboxes.scripts.utils.helpers import get_user_helper

def get_pro_not_validated_user():
    query = User.query.filter(User.UserOfferers.any())
    query = query.filter(User.validationToken != None)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
