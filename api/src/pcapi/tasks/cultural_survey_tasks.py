import datetime
import json

import pydantic

from pcapi import settings
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.object_storage.backends import gcp as gcp_backend
from pcapi.tasks.decorator import task


CULTURAL_SURVEY_ANSWERS_QUEUE_NAME = settings.GCP_CULTURAL_SURVEY_ANSWERS_QUEUE_NAME


class CulturalSurveyTaskAnswer(pydantic.BaseModel):
    question_id: cultural_survey_models.CulturalSurveyQuestionEnum
    answer_ids: list[cultural_survey_models.CulturalSurveyAnswerEnum]

    class Config:
        use_enum_values = True


class CulturalSurveyTaskAnswers(pydantic.BaseModel):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[CulturalSurveyTaskAnswer]


@task(CULTURAL_SURVEY_ANSWERS_QUEUE_NAME, "/cultural_survey/upload_answers")
def upload_answers_task(payload: CulturalSurveyTaskAnswers) -> None:
    BUCKET_NAME = settings.GCP_DATA_BUCKET_NAME
    PROJECT_ID = settings.GCP_DATA_PROJECT_ID

    STORAGE_PATH = f"QPI_exports/qpi_answers_{datetime.date.today().strftime('%Y%m%d')}"
    answers_file_name = f"user_id_{payload.user_id}.jsonl"
    gcp_client = gcp_backend.GCPBackend(bucket_name=BUCKET_NAME, project_id=PROJECT_ID)

    answer = {
        "user_id": payload.user_id,
        "submitted_at": payload.submitted_at.isoformat(),
        "answers": [answer.dict() for answer in payload.answers],
    }

    gcp_client.store_public_object(
        folder=STORAGE_PATH,
        object_id=answers_file_name,
        blob=bytes(json.dumps(answer, ensure_ascii=False), "utf-8"),
        content_type="application/json",
    )
