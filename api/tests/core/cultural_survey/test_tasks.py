from unittest.mock import patch

from pcapi import settings
from pcapi.core.cultural_survey import tasks
from pcapi.utils import date as date_utils


class CulturalSurveyAnswerTest:
    @patch("pcapi.core.cultural_survey.tasks.store_public_object")
    def test_cultural_survey_task(self, store_public_object_mock, client, db_session):
        submit_time = date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S")
        submit_time_short = date_utils.get_naive_utc_now().strftime("%Y%m%d")

        tasks.upload_answers_task.run(
            tasks.CulturalSurveyTaskAnswers(
                user_id=1,
                submitted_at=submit_time,
                answers=[
                    {"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]},
                    {"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]},
                ],
            )
        )

        answers_bytes = f'{{"user_id": 1, "submitted_at": "{submit_time}", "answers": [{{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}}, {{"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]}}]}}'.encode()

        store_public_object_mock.assert_called_once_with(
            folder=f"QPI_exports/qpi_answers_{submit_time_short}",
            object_id="user_id_1.jsonl",
            blob=answers_bytes,
            content_type="application/json",
            bucket=settings.GCP_DATA_BUCKET_NAME,
            project_id=settings.GCP_DATA_PROJECT_ID,
        )
