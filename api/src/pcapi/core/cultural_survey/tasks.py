import datetime
import json

from pydantic import BaseModel as BaseModelV2
from pydantic import ConfigDict

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.object_storage import store_public_object


class CulturalSurveyTaskAnswer(BaseModelV2):
    question_id: cultural_survey_models.CulturalSurveyQuestionEnum
    answer_ids: list[cultural_survey_models.CulturalSurveyAnswerEnum]

    model_config = ConfigDict(
        use_enum_values=True,
    )


class CulturalSurveyTaskAnswers(BaseModelV2):
    user_id: int
    submitted_at: datetime.datetime
    answers: list[CulturalSurveyTaskAnswer]


@celery_async_task(
    name="tasks.cultural_survey.default.upload_answers",
    model=CulturalSurveyTaskAnswers,
    max_per_time_window=8,
    time_window_size=1,
)
def upload_answers_task(payload: CulturalSurveyTaskAnswers) -> None:
    storage_path = f"QPI_exports/qpi_answers_{datetime.date.today().strftime('%Y%m%d')}"
    answers_file_name = f"user_id_{payload.user_id}.jsonl"

    answer = {
        "user_id": payload.user_id,
        "submitted_at": payload.submitted_at.isoformat(),
        "answers": [answer.model_dump() for answer in payload.answers],
    }

    store_public_object(
        folder=storage_path,
        object_id=answers_file_name,
        blob=bytes(json.dumps(answer, ensure_ascii=False), "utf-8"),
        content_type="application/json",
        bucket=settings.GCP_DATA_BUCKET_NAME,
        project_id=settings.GCP_DATA_PROJECT_ID,
    )
