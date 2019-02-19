from models.user import User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_existing_webapp_hnmm_user():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('has-no-more-money'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_hbs_user():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }
