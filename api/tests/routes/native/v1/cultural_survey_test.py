import datetime
from unittest.mock import patch

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.cultural_survey.models import CulturalSurveyAnswerEnum
from pcapi.core.cultural_survey.models import CulturalSurveyQuestionEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing
from pcapi.utils import date as date_utils
from pcapi.utils.string import u_nbsp


pytestmark = pytest.mark.usefixtures("db_session")


class CulturalSurveyQuestionsTest:
    def test_get_cultural_survey_questions(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user)
        with assert_num_queries(1):  # user
            response = client.get("/native/v1/cultural_survey/questions")
            assert response.status_code == 200

        assert response.json == {
            "questions": [
                {
                    "id": "SORTIES",
                    "title": f"Au cours de l'année précédente, tu as été au moins une fois{u_nbsp}...",
                    "answers": [
                        {
                            "id": "FESTIVAL",
                            "title": "À un festival",
                            "sub_question": "FESTIVALS",
                            "subtitle": None,
                        },
                        {
                            "id": "SPECTACLE",
                            "title": "À un spectacle",
                            "subtitle": "(pièce de théâtre, cirque, danse...)",
                            "sub_question": "SPECTACLES",
                        },
                        {
                            "id": "BIBLIOTHEQUE",
                            "title": "À la bibliothèque",
                            "subtitle": "ou à la médiathèque",
                            "sub_question": None,
                        },
                        {
                            "id": "EVENEMENT_JEU",
                            "title": "À un escape game",
                            "subtitle": "ou participé à un jeu, jeu concours",
                            "sub_question": None,
                        },
                        {"id": "CONCERT", "title": "À un concert", "subtitle": None, "sub_question": None},
                        {"id": "CINEMA", "title": "Au cinéma", "subtitle": None, "sub_question": None},
                        {
                            "id": "MUSEE",
                            "title": "Au musée,",
                            "subtitle": "un monument, une exposition...",
                            "sub_question": None,
                        },
                        {
                            "id": "CONFERENCE",
                            "title": "À une conférence,",
                            "subtitle": "une rencontre ou une découverte des métiers de la Culture",
                            "sub_question": None,
                        },
                        {
                            "id": "COURS",
                            "title": "À un cours",
                            "subtitle": "(danse, théâtre, musique, dessin...)",
                            "sub_question": None,
                        },
                        {
                            "id": "SANS_SORTIES",
                            "title": "Aucune de ces sorties culturelles",
                            "subtitle": None,
                            "sub_question": None,
                        },
                    ],
                },
                {
                    "id": "FESTIVALS",
                    "title": f"À quels types de festivals as-tu participé{u_nbsp}?",
                    "answers": [
                        {
                            "id": "FESTIVAL_MUSIQUE",
                            "title": "Festival de musique",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "FESTIVAL_AVANT_PREMIERE",
                            "title": "Avant-première de film",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "FESTIVAL_SPECTACLE",
                            "title": "Festival de danse, de cirque",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "FESTIVAL_LIVRE",
                            "title": "Festival littéraire",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "FESTIVAL_CINEMA",
                            "title": "Festival de cinéma",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {"id": "FESTIVAL_AUTRE", "title": "Autre festival", "subtitle": None, "sub_question": None},
                    ],
                },
                {
                    "id": "SPECTACLES",
                    "title": f"À quels types de spectacles as-tu assisté{u_nbsp}?",
                    "answers": [
                        {
                            "id": "SPECTACLE_HUMOUR",
                            "title": "Spectacle d'humour",
                            "subtitle": "ou café-théâtre",
                            "sub_question": None,
                        },
                        {"id": "SPECTACLE_THEATRE", "title": "Théâtre", "subtitle": None, "sub_question": None},
                        {"id": "SPECTACLE_RUE", "title": "Spectacle de rue", "subtitle": None, "sub_question": None},
                        {
                            "id": "SPECTACLE_OPERA",
                            "title": "Comédie musicale, opéra",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {"id": "SPECTACLE_CIRQUE", "title": "Cirque", "subtitle": None, "sub_question": None},
                        {
                            "id": "SPECTACLE_DANSE",
                            "title": "Spectacle de danse",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {"id": "SPECTACLE_AUTRE", "title": "Autres spectacles", "subtitle": None, "sub_question": None},
                    ],
                },
                {
                    "id": "ACTIVITES",
                    "title": f"Au cours de l'année précédente, tu as au moins une fois{u_nbsp}...",
                    "answers": [
                        {
                            "id": "MATERIEL_ART_CREATIF",
                            "title": "Utilisé du matériel d'art",
                            "subtitle": "pour peindre, dessiner...",
                            "sub_question": None,
                        },
                        {"id": "PODCAST", "title": "Écouté un podcast", "subtitle": None, "sub_question": None},
                        {"id": "LIVRE", "title": "Lu un livre", "subtitle": None, "sub_question": None},
                        {
                            "id": "JOUE_INSTRUMENT",
                            "title": "Joué d'un instrument de musique ",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "PRESSE_EN_LIGNE",
                            "title": "Lu un article de presse",
                            "subtitle": "en ligne",
                            "sub_question": None,
                        },
                        {"id": "JEU_VIDEO", "title": "Joué à un jeu vidéo", "subtitle": None, "sub_question": None},
                        {
                            "id": "FILM_DOMICILE",
                            "title": "Regardé un film chez toi",
                            "subtitle": None,
                            "sub_question": None,
                        },
                        {
                            "id": "SANS_ACTIVITES",
                            "title": "Aucune de ces activités culturelles",
                            "subtitle": None,
                            "sub_question": None,
                        },
                    ],
                },
                {
                    "id": "PROJECTIONS",
                    "title": f"Cette année, tu aimerais{u_nbsp}...",
                    "answers": [
                        {
                            "id": "PROJECTION_FESTIVAL",
                            "title": "Aller à un festival",
                            "sub_question": None,
                            "subtitle": "Musique, cinéma, littéraire...",
                        },
                        {
                            "id": "PROJECTION_CINEMA",
                            "title": "Aller au cinéma",
                            "sub_question": None,
                            "subtitle": None,
                        },
                        {
                            "id": "PROJECTION_VISITE",
                            "title": "Faire des visites",
                            "sub_question": None,
                            "subtitle": "Une exposition, un monument...",
                        },
                        {
                            "id": "PROJECTION_CONCERT",
                            "title": "Participer à un concert",
                            "sub_question": None,
                            "subtitle": None,
                        },
                        {
                            "id": "PROJECTION_CD_VINYLE",
                            "title": "Écouter des CDs ou des vinyls",
                            "sub_question": None,
                            "subtitle": None,
                        },
                        {
                            "id": "PROJECTION_SPECTACLE",
                            "title": "Voir un spectacle",
                            "sub_question": None,
                            "subtitle": "Pièce de théâtre, cirque, humour...",
                        },
                        {
                            "id": "PROJECTION_ACTIVITE_ARTISTIQUE",
                            "title": "Faire une activité artistique",
                            "sub_question": None,
                            "subtitle": "Dessin, danse, théâtre, musique...",
                        },
                        {
                            "id": "PROJECTION_LIVRE",
                            "title": "Lire des livres",
                            "sub_question": None,
                            "subtitle": None,
                        },
                        {
                            "id": "PROJECTION_CONFERENCE",
                            "title": "Assister à des conférences ou des rencontres",
                            "sub_question": None,
                            "subtitle": None,
                        },
                        {
                            "id": "PROJECTION_JEU",
                            "title": "Faire des jeux en solo ou en duo",
                            "sub_question": None,
                            "subtitle": "Escape games, jeux vidéo...",
                        },
                        {
                            "id": "PROJECTION_AUTRE",
                            "title": "Autre",
                            "sub_question": None,
                            "subtitle": None,
                        },
                    ],
                },
            ]
        }

    @time_machine.travel("2020-01-01", tick=False)
    @patch("pcapi.tasks.cultural_survey_tasks.store_public_object")
    def test_post_cultural_survey_answers(self, store_public_object_mock, client):
        user: users_models.User = users_factories.UserFactory()
        client.with_token(user)

        all_answers = [
            {
                "questionId": CulturalSurveyQuestionEnum.SORTIES.value,
                "answerIds": [
                    CulturalSurveyAnswerEnum.FESTIVAL.value,
                ],
            },
            {
                "questionId": CulturalSurveyQuestionEnum.FESTIVALS.value,
                "answerIds": [
                    CulturalSurveyAnswerEnum.FESTIVAL_MUSIQUE.value,
                ],
            },
            {
                "questionId": CulturalSurveyQuestionEnum.PROJECTIONS.value,
                "answerIds": [
                    CulturalSurveyAnswerEnum.PROJECTION_SPECTACLE.value,
                    CulturalSurveyAnswerEnum.PROJECTION_CINEMA.value,
                ],
            },
        ]
        response = client.post(
            "/native/v1/cultural_survey/answers",
            json={"answers": all_answers},
        )

        assert response.status_code == 204

        answers_str = (
            '{"user_id": %s, "submitted_at": "2020-01-01T00:00:00", "answers": '
            '[{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}, '
            '{"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]}, '
            '{"question_id": "PROJECTIONS", "answer_ids": ["PROJECTION_SPECTACLE", "PROJECTION_CINEMA"]}]}'
        ) % user.id

        store_public_object_mock.assert_called_once_with(
            folder="QPI_exports/qpi_answers_20200101",
            object_id=f"user_id_{user.id}.jsonl",
            blob=bytes(answers_str, "utf-8"),
            content_type="application/json",
            bucket=settings.GCP_DATA_BUCKET_NAME,
            project_id=settings.GCP_DATA_PROJECT_ID,
        )

        assert not user.needsToFillCulturalSurvey
        assert user.culturalSurveyFilledDate == date_utils.get_naive_utc_now()

        assert len(testing.sendinblue_requests) == 1
        assert testing.sendinblue_requests[0]["email"] == user.email
        assert (
            testing.sendinblue_requests[0]["attributes"]["INTENDED_CATEGORIES"]
            == "PROJECTION_SPECTACLE,PROJECTION_CINEMA"
        )
