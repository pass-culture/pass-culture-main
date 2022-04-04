import datetime
from unittest.mock import patch

import freezegun

from pcapi.core.cultural_survey import cultural_survey
from pcapi.tasks.cultural_survey_tasks import upload_answers_task
from pcapi.tasks.serialization import cultural_survey_tasks as serializers


class CulturalSurveyTasksTest:
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    @freezegun.freeze_time("2020-01-01")
    def test_upload_answers_task(self, store_public_object):
        answers = [
            {
                "question_id": cultural_survey.SORTIES.id,
                "choices": [cultural_survey.FESTIVAL.id],
            },
            {
                "question_id": cultural_survey.FESTIVALS.id,
                "choices": [cultural_survey.FESTIVAL_LIVRE.id],
            },
        ]

        payload = serializers.CulturalSurveyAnswersForData(
            user_id=1,
            submitted_at=datetime.datetime.utcnow().isoformat(),
            answers=answers,
        )
        upload_answers_task(payload)

        answers_str = (
            '[{"question_id": "SORTIES", "choices": ["FESTIVAL"]}, '
            '{"question_id": "FESTIVALS", "choices": ["FESTIVAL_LIVRE"]}]'
        )

        # Note: if the path does not exist, GCP creates the necessary folders
        store_public_object.assert_called_once_with(
            folder="QPI_exports/qpi_answers_20200101",
            object_id="user_id_1.jsonl",
            blob=bytes(answers_str, "utf-8"),
            content_type="application/json",
        )
