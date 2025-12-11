import logging

from flask_login import current_user

from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.external.attributes.api import update_external_user
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.tasks.cultural_survey_tasks import upload_answers_task
from pcapi.tasks.serialization.cultural_survey_tasks import CulturalSurveyAnswersForData
from pcapi.utils import date as date_utils
from pcapi.utils.repository import transaction

from .. import blueprint
from .serialization import cultural_survey as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/cultural_survey/questions", methods=["GET"])
@spectree_serialize(
    response_model=serializers.CulturalSurveyQuestionsResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_cultural_survey_questions() -> serializers.CulturalSurveyQuestionsResponse:
    return serializers.CulturalSurveyQuestionsResponse(
        questions=cultural_survey.ALL_CULTURAL_SURVEY_QUESTIONS,
    )


@blueprint.native_route("/cultural_survey/answers", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)
@authenticated_and_active_user_required
def post_cultural_survey_answers(body: serializers.CulturalSurveyAnswersRequest) -> None:
    payload = CulturalSurveyAnswersForData(
        user_id=current_user.id,
        submitted_at=date_utils.get_naive_utc_now().isoformat(),  # type: ignore[arg-type]
        answers=body.answers,
    )

    upload_answers_task.delay(payload)
    with transaction():
        current_user.needsToFillCulturalSurvey = False
        current_user.culturalSurveyFilledDate = date_utils.get_naive_utc_now()

    update_external_user(
        current_user,
        cultural_survey_answers={answer.question_id: answer.answer_ids for answer in body.answers},  # type: ignore[misc]
    )
