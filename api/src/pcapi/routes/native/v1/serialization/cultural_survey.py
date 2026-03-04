import pydantic

from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class CulturalSurveyQuestionsResponse(HttpBodyModel):
    questions: list[cultural_survey.CulturalSurveyQuestion]

    model_config = pydantic.ConfigDict(
        alias_generator=None,
    )


class CulturalSurveyUserAnswer(HttpBodyModel):
    question_id: cultural_survey_models.CulturalSurveyQuestionEnum
    answer_ids: list[cultural_survey_models.CulturalSurveyAnswerEnum]

    model_config = pydantic.ConfigDict(
        use_enum_values=True,
    )


class CulturalSurveyAnswersRequest(HttpQueryParamsModel):
    answers: list[CulturalSurveyUserAnswer]
