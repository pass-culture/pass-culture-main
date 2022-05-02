import datetime
from unittest.mock import patch

import freezegun

from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.tasks.cultural_survey_tasks import upload_answers_task
from pcapi.tasks.serialization import cultural_survey_tasks as serializers


class CulturalSurveyTasksTest:
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    @freezegun.freeze_time("2020-01-01")
    def test_upload_answers_task(self, store_public_object):
        answers = [
            {
                "questionId": cultural_survey_models.CulturalSurveyQuestionEnum.SORTIES,
                "answerIds": [
                    cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL,
                ],
            },
            {
                "questionId": cultural_survey_models.CulturalSurveyQuestionEnum.FESTIVALS,
                "answerIds": [
                    cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL_LIVRE,
                ],
            },
        ]

        payload = serializers.CulturalSurveyAnswersForData(
            user_id=1,
            submitted_at=datetime.datetime.utcnow().isoformat(),
            answers=answers,
        )
        upload_answers_task(payload)

        answers_str = (
            '{"user_id": 1, "submitted_at": "2020-01-01T00:00:00", "answers": '
            '[{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}, '
            '{"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_LIVRE"]}]}'
        )

        # Note: if the path does not exist, GCP creates the necessary folders
        store_public_object.assert_called_once_with(
            folder="QPI_exports/qpi_answers_20200101",
            object_id="user_id_1.jsonl",
            blob=bytes(answers_str, "utf-8"),
            content_type="application/json",
        )
