import datetime

import pydantic


class CulturalSurveyAnswersForData(pydantic.BaseModel):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[dict]
