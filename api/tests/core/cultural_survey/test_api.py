import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.cultural_survey import tasks
from pcapi.core.cultural_survey.api import save_cultural_survey_for_user
from pcapi.core.cultural_survey.models import UserCulturalSurvey
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


class CulturalSurveyAnswerTest:
    def test_should_save_a_cultural_survey_for_user(self, db_session):
        submit_time = date_utils.get_naive_utc_now().isoformat()

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

        has_count = db_session.query(UserCulturalSurvey).filter_by(userId=user.id).count()
        assert has_count == 1

    def test_should_raise_an_exception_for_submitting_twice_the_survey(self, db_session):
        submit_time = date_utils.get_naive_utc_now().isoformat()

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
