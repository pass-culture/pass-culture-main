from models.booking import Booking
from models.recommendation import Recommendation
from models.user import User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper, get_recommendation_helper

def get_existing_webapp_user_with_no_date_read():
    query = filter_webapp_users(User.query)
    query = query.filter(
        ~User.recommendations.any(
            Recommendation.dateRead != None
        )
    )
    user = query.first()


    return {
        "user": get_user_helper(user),
    }

def get_existing_webapp_user_with_at_least_one_recommendation():
    query = filter_webapp_users(User.query)
    query = query.filter(
        User.recommendations.any()
    )
    user = query.first()
    recommendation = user.recommendations[0]



    return {
        "user": get_user_helper(user),
        "recommendation": get_recommendation_helper(recommendation)
    }


def get_existing_webapp_user_with_bookings():
    query = filter_webapp_users(User.query)
    query = query.join(Booking)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
