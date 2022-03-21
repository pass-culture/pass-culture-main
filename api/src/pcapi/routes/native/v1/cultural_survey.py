import logging

from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.users import models as users_models
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import cultural_survey as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/cultural_survey/questions", methods=["GET"])
@spectree_serialize(
    response_model=serializers.CulturalSurveyQuestionsResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def get_cultural_survey_questions(user: users_models.User) -> serializers.CulturalSurveyQuestionsResponse:
    return serializers.CulturalSurveyQuestionsResponse(
        questions=cultural_survey.ALL_CULTURAL_SURVEY_QUESTIONS,
    )
