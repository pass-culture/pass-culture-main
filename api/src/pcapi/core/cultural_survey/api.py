import logging

from pcapi.core.cultural_survey.models import UserCulturalSurvey
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def save_cultural_survey_for_user(
    user: User,
    survey_data: list[dict],
) -> UserCulturalSurvey:
    """
    Save answers from a cultural survey to an user.

    This save should be done once, and there will be no overwriting for
    the moment.
    """
    cultural_survey = UserCulturalSurvey(
        userId=user.id,
        answers=survey_data,
    )

    db.session.add(cultural_survey)
    db.session.flush()

    logger.info(
        "Cultural Survey saved",
        extra={"user_id": user.id},
        technical_message_id="cultural_survey.saved",
    )

    return cultural_survey
