import datetime
import json

from pcapi import settings
from pcapi.core.object_storage.backends import gcp as gcp_backend
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization import cultural_survey_tasks as serializers


CULTURAL_SURVEY_ANSWERS_QUEUE_NAME = settings.GCP_CULTURAL_SURVEY_ANSWERS_QUEUE_NAME


@task(CULTURAL_SURVEY_ANSWERS_QUEUE_NAME, "/cultural_survey/upload_answers")
def upload_answers_task(payload: serializers.CulturalSurveyAnswersForData) -> None:
    BUCKET_NAME = settings.GCP_DATA_BUCKET_NAME
    PROJECT_ID = settings.GCP_DATA_PROJECT_ID

    STORAGE_PATH = f"QPI_exports/qpi_answers_{datetime.date.today().strftime('%Y%m%d')}"
    answers_file_name = f"user_id_{payload.user_id}.jsonl"
    gcp_client = gcp_backend.GCPBackend(bucket_name=BUCKET_NAME, project_id=PROJECT_ID)

    answer = {
        "user_id": payload.user_id,
        "submitted_at": payload.submitted_at.isoformat(),
        "answers": [payload_answer.dict() for payload_answer in payload.answers],
    }

    gcp_client.store_public_object(
        folder=STORAGE_PATH,
        object_id=answers_file_name,
        blob=bytes(json.dumps(answer, ensure_ascii=False), "utf-8"),
        content_type="application/json",
    )
