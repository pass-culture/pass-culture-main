from pcapi.core.users.models import User
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_existing_webapp_validated_user_with_has_filled_cultural_survey():
    query = keep_only_webapp_users(User.query)
    query = query.filter_by(needsToFillCulturalSurvey=False, hasSeenTutorials=True, isEmailValidated=True)
    user = query.first()

    return {"user": get_beneficiary_helper(user)}
