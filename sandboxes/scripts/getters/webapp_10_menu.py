from models.user import UserSQLEntity
from repository.user_queries import keep_only_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper

def get_existing_webapp_validated_user_with_has_filled_cultural_survey():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter_by(
        needsToFillCulturalSurvey=False,
        resetPasswordToken=None,
        hasSeenTutorials=True
    )
    user = query.first()

    return {
        "user": get_user_helper(user)
    }
