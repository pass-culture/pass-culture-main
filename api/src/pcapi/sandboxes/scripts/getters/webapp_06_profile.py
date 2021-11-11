from pcapi.core.users.models import User
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_existing_webapp_user_can_book_thing_offer():
    query = keep_only_webapp_users(User.query)
    query = query.filter(User.email.contains("93.has-booked-some"))
    user = query.first()
    return {"user": get_beneficiary_helper(user)}
