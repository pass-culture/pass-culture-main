from random import randrange

import factory
from factory.fuzzy import FuzzyChoice

from pcapi.core.cultural_survey.cultural_survey import SURVEY_QUESTIONS_AND_ANSWERS
from pcapi.core.cultural_survey.models import UserCulturalSurvey
from pcapi.core.factories import BaseFactory
from pcapi.core.users.factories import UserFactory


class UserCulturalSurveyFactory(BaseFactory):
    class Meta:
        model = UserCulturalSurvey

    user = factory.SubFactory(UserFactory)
    answers = factory.lazy_attribute(
        lambda _: [
            {
                "question_id": question.id,
                "answers_id": [FuzzyChoice(answers).fuzz() for _ in range(randrange(len(answers)))],
            }
            for question, answers in SURVEY_QUESTIONS_AND_ANSWERS
        ],
    )
