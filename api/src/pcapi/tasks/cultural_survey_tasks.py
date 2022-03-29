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
    today = datetime.date.today().strftime("%Y%m%d")

    STORAGE_PATH = BUCKET_NAME + f"/QPI_exports/qpi_answers_{today}/"
    answers_file_name = STORAGE_PATH + f"{payload.user_id}.jsonl"
    gcp_client = gcp_backend.GCPBackend(BUCKET_NAME, PROJECT_ID)

    gcp_client.store_public_object(
        folder=BUCKET_NAME,
        object_id=answers_file_name,
        blob=bytes(json.dumps(payload.answers, ensure_ascii=False), "utf-8"),
        content_type="application/json",
    )
