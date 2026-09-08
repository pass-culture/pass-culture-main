import logging

from pcapi.core.cultural_survey.models import UserCulturalSurvey
from pcapi.core.cultural_survey.tasks import CulturalSurveyTaskAnswers
from pcapi.models import db


logger = logging.getLogger(__name__)


def save_cultural_survey_for_user(payload: CulturalSurveyTaskAnswers) -> UserCulturalSurvey:
    """Save answers from a cultural survey to an user.

    This save should be done once, and there will be no overwriting for
    the moment.
    """
    cultural_survey = UserCulturalSurvey(
        userId=payload.user_id,
        answers=[answer.model_dump() for answer in payload.answers],
    )

    db.session.add(cultural_survey)
    db.session.flush()

    logger.info(
        "Cultural Survey saved",
        extra={"user_id": payload.user_id},
        technical_message_id="cultural_survey.saved",
    )

    return cultural_survey
