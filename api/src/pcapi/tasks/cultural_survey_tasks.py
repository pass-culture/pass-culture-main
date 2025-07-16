import datetime
import json

import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.object_storage import store_public_object
from pcapi.tasks.decorator import task


CULTURAL_SURVEY_ANSWERS_QUEUE_NAME = settings.GCP_CULTURAL_SURVEY_ANSWERS_QUEUE_NAME


class CulturalSurveyTaskAnswer(pydantic_v1.BaseModel):
    question_id: cultural_survey_models.CulturalSurveyQuestionEnum
    answer_ids: list[cultural_survey_models.CulturalSurveyAnswerEnum]

    class Config:
        use_enum_values = True


class CulturalSurveyTaskAnswers(pydantic_v1.BaseModel):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[CulturalSurveyTaskAnswer]


@task(CULTURAL_SURVEY_ANSWERS_QUEUE_NAME, "/cultural_survey/upload_answers")
def upload_answers_task(payload: CulturalSurveyTaskAnswers) -> None:
    storage_path = f"QPI_exports/qpi_answers_{datetime.date.today().strftime('%Y%m%d')}"
    answers_file_name = f"user_id_{payload.user_id}.jsonl"

    answer = {
        "user_id": payload.user_id,
        "submitted_at": payload.submitted_at.isoformat(),
        "answers": [answer.dict() for answer in payload.answers],
    }

    store_public_object(
        folder=storage_path,
        object_id=answers_file_name,
        blob=bytes(json.dumps(answer, ensure_ascii=False), "utf-8"),
        content_type="application/json",
        bucket=settings.GCP_DATA_BUCKET_NAME,
        project_id=settings.GCP_DATA_PROJECT_ID,
    )
