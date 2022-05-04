from unittest.mock import patch

import freezegun

from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


class CulturalSurveyAnswerTest:
    @freezegun.freeze_time("2020-01-01")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_cultural_survey_task(self, store_public_object, client, db_session):
        data = {
            "user_id": 1,
            "submitted_at": "2020-01-01T00:00:00",
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

        answers_bytes = b'{"user_id": 1, "submitted_at": "2020-01-01T00:00:00", "answers": [{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}, {"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]}]}'

        assert response.status_code == 204
        store_public_object.assert_called_once_with(
            folder="QPI_exports/qpi_answers_20200101",
            object_id="user_id_1.jsonl",
            blob=answers_bytes,
            content_type="application/json",
        )
