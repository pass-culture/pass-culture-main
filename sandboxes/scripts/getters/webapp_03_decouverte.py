from models.booking_sql_entity import BookingSQLEntity
from models.offer_sql_entity import OfferSQLEntity
from models.recommendation import Recommendation
from models.user_sql_entity import UserSQLEntity
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_beneficiary_helper, get_recommendation_helper


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
        "user": get_beneficiary_helper(user),
    }


def get_existing_webapp_user_with_at_least_one_recommendation():
    query = Recommendation.query.join(UserSQLEntity)
    query = keep_only_webapp_users(query)
    query = query.reset_joinpoint().join(OfferSQLEntity)

    recommendation = query.first()
    return {
        "user": get_beneficiary_helper(recommendation.user),
        "recommendation": get_recommendation_helper(recommendation)
    }


def get_existing_webapp_user_with_bookings():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.join(BookingSQLEntity)
    user = query.first()

    return {
        "user": get_beneficiary_helper(user)
    }
