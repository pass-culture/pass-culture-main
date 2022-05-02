import datetime

import pydantic

from pcapi.routes.native.v1.serialization.cultural_survey import CulturalSurveyUserAnswer


class CulturalSurveyAnswersForData(pydantic.BaseModel):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[CulturalSurveyUserAnswer]
