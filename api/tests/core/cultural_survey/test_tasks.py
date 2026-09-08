from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from pcapi import settings
from pcapi.core.cultural_survey import tasks
from pcapi.core.cultural_survey.api import save_cultural_survey_for_user
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


class CulturalSurveyAnswerTest:
    def test_should_save_a_cultural_survey_for_user(self, db_session):
        submit_time = date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S")

        user = users_factories.UserFactory.create()
        db_session.add(user)
        db_session.flush()

        payload = tasks.CulturalSurveyTaskAnswers(
            user_id=user.id,
            submitted_at=submit_time,
            answers=[
                {"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]},
                {"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]},
            ],
        )

        response = save_cultural_survey_for_user(payload)

        assert response

    def test_should_raise_an_exception_for_submitting_twice_the_survey(self, db_session):
        submit_time = date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S")

        user = users_factories.UserFactory.create()
        db_session.add(user)
        db_session.flush()

        payload = tasks.CulturalSurveyTaskAnswers(
            user_id=user.id,
            submitted_at=submit_time,
            answers=[
                {"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]},
                {"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]},
            ],
        )

        save_cultural_survey_for_user(payload)

        with pytest.raises(IntegrityError):
            save_cultural_survey_for_user(payload)

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
