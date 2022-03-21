from pcapi.core.cultural_survey.cultural_survey import CulturalSurveyQuestion
from pcapi.routes.serialization import BaseModel


class CulturalSurveyQuestionsResponse(BaseModel):
    questions: list[CulturalSurveyQuestion]
