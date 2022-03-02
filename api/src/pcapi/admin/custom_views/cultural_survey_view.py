from dataclasses import fields

from flask import Response
from flask_admin import expose

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.core.cultural_survey.cultural_survey import ALL_CULTURAL_SURVEY_ANSWERS
from pcapi.core.cultural_survey.cultural_survey import ALL_CULTURAL_SURVEY_QUESTIONS
from pcapi.core.cultural_survey.cultural_survey import CulturalSurveyAnswer


class CulturalSurveyView(BaseCustomAdminView):
    @expose("/", methods=["GET"])
    def cultural_survey(self) -> Response:
        answers_column_names = [field.name for field in fields(CulturalSurveyAnswer)]
        column_names = ["Question"]
        column_names += answers_column_names

        column_labels = {
            "id": "Clé de réponse",
            "sub_question": "Déclenche la sous-question suivante",
            "title": "Titre",
            "subtitle": "Sous-titre",
        }

        return self.render(
            "admin/cultural_survey.html",
            questions=ALL_CULTURAL_SURVEY_QUESTIONS,
            answers=ALL_CULTURAL_SURVEY_ANSWERS,
            column_names=column_names,
            answers_column_names=answers_column_names,
            column_labels=column_labels,
        )
