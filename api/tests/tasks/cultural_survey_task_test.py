from datetime import datetime
from unittest.mock import patch

from pcapi import settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


class CulturalSurveyAnswerTest:
    @patch("pcapi.tasks.cultural_survey_tasks.store_public_object")
    def test_cultural_survey_task(self, store_public_object_mock, client, db_session):
        submit_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        submit_time_short = datetime.utcnow().strftime("%Y%m%d")
        data = {
            "user_id": 1,
            "submitted_at": submit_time,
            "answers": [
                {"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]},
                {"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]},
            ],
        }

        response = client.post(
            "/cloud-tasks/cultural_survey/upload_answers",
            json=data,
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        answers_bytes = f'{{"user_id": 1, "submitted_at": "{submit_time}", "answers": [{{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}}, {{"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]}}]}}'.encode()

        assert response.status_code == 204
        store_public_object_mock.assert_called_once_with(
            folder=f"QPI_exports/qpi_answers_{submit_time_short}",
            object_id="user_id_1.jsonl",
            blob=answers_bytes,
            content_type="application/json",
            bucket=settings.GCP_DATA_BUCKET_NAME,
            project_id=settings.GCP_DATA_PROJECT_ID,
        )
