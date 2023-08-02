import datetime

import pydantic.v1 as pydantic_v1

from pcapi.routes.native.v1.serialization.cultural_survey import CulturalSurveyUserAnswer


class CulturalSurveyAnswersForData(pydantic_v1.BaseModel):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[CulturalSurveyUserAnswer]
