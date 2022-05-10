import datetime
import logging

from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.users import models as users_models
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.tasks.cultural_survey_tasks import upload_answers_task
from pcapi.tasks.serialization.cultural_survey_tasks import CulturalSurveyAnswersForData

from . import blueprint
from .serialization import cultural_survey as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/cultural_survey/questions", methods=["GET"])
@spectree_serialize(
    response_model=serializers.CulturalSurveyQuestionsResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_cultural_survey_questions(user: users_models.User) -> serializers.CulturalSurveyQuestionsResponse:
    return serializers.CulturalSurveyQuestionsResponse(
        questions=cultural_survey.ALL_CULTURAL_SURVEY_QUESTIONS,
    )


@blueprint.native_v1.route("/cultural_survey/answers", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)
@authenticated_and_active_user_required
def post_cultural_survey_answers(user: users_models.User, body: serializers.CulturalSurveyAnswersRequest) -> None:
    payload = CulturalSurveyAnswersForData(
        user_id=user.id,
        submitted_at=datetime.datetime.utcnow().isoformat(),
        answers=body.answers,
    )

    upload_answers_task.delay(payload)
    with transaction():
        user.needsToFillCulturalSurvey = False
        user.culturalSurveyFilledDate = datetime.datetime.utcnow()
