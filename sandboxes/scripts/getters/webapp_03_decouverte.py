from models.booking import Booking
from models.offer import Offer
from models.recommendation import Recommendation
from models.user import UserSQLEntity
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper, get_recommendation_helper


def get_existing_webapp_user_with_no_date_read():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter_by(
        needsToFillCulturalSurvey=False,
        resetPasswordToken=None,
        hasSeenTutorials=True
    )
    query = query.filter(
        ~UserSQLEntity.recommendations.any(
            Recommendation.dateRead != None
        )
    )
    user = query.first()


    return {
        "user": get_user_helper(user),
    }

def get_existing_webapp_user_with_at_least_one_recommendation():
    query = Recommendation.query.join(UserSQLEntity)
    query = keep_only_webapp_users(query)
    query = query.reset_joinpoint().join(Offer)

    recommendation = query.first()
    return {
        "user": get_user_helper(recommendation.user),
        "recommendation": get_recommendation_helper(recommendation)
    }


def get_existing_webapp_user_with_bookings():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.join(Booking)
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
