from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class CulturalSurveyQuestionsResponse(BaseModel):
    questions: list[cultural_survey.CulturalSurveyQuestion]


class CulturalSurveyUserAnswer(BaseModel):
    question_id: cultural_survey_models.CulturalSurveyQuestionEnum
    answer_ids: list[cultural_survey_models.CulturalSurveyAnswerEnum]

    class Config:
        alias_generator = to_camel
        use_enum_values = True


class CulturalSurveyAnswersRequest(BaseModel):
    answers: list[CulturalSurveyUserAnswer]
