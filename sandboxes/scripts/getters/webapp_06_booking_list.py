from models.user import User
from models.booking import Booking
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper


def get_existing_webapp_user_with_bookings():
    query = keep_only_webapp_users(User.query)
    query = query.reset_joinpoint().join(Booking)
    user = query.first()
    return {
        "user": get_user_helper(user)
    }
