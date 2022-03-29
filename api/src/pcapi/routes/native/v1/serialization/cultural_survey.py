from pydantic import root_validator

from pcapi.core.cultural_survey import cultural_survey
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class CulturalSurveyQuestionsResponse(BaseModel):
    questions: list[cultural_survey.CulturalSurveyQuestion]


class CulturalSurveyUserAnswer(BaseModel):
    question_id: str
    answer_ids: list[str]

    class Config:
        alias_generator = to_camel

    @root_validator(pre=True)
    def check_answer_ids_are_valid(cls, values: dict) -> dict:  # pylint: disable=no-self-argument
        for value in values.get("answer_ids", []):
            if not value in cultural_survey.CulturalSurveyAnswersDict:
                raise ValueError(f"Invalid answer id: {value}")
        return values


class CulturalSurveyAnswersRequest(BaseModel):
    answers: list[CulturalSurveyUserAnswer]
