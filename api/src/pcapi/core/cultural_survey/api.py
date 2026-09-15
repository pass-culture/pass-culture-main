import logging

from sqlalchemy.dialects.postgresql import insert

from pcapi.core.cultural_survey.models import UserCulturalSurvey
from pcapi.core.cultural_survey.tasks import CulturalSurveyTaskAnswers
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now


logger = logging.getLogger(__name__)


def save_cultural_survey_for_user(payload: CulturalSurveyTaskAnswers) -> None:
    answers = [answer.model_dump() for answer in payload.answers]

    stmt = (
        insert(UserCulturalSurvey)
        .values(userId=payload.user_id, answers=answers)
        .on_conflict_do_update(
            constraint="user_cultural_survey_userId_unique",
            set_={
                "answers": answers,
                "createdAt": get_naive_utc_now(),
            },
        )
    )

    db.session.execute(stmt)
    db.session.flush()

    logger.info(
        "Cultural Survey saved",
        extra={"user_id": payload.user_id},
        technical_message_id="cultural_survey.saved",
    )
