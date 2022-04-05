import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.core.cultural_survey import cultural_survey
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.tasks.serialization import cultural_survey_tasks as serializers


pytestmark = pytest.mark.usefixtures("db_session")


class CulturalSurveyQuestionsTest:
    def test_get_cultural_survey_questions(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)
        response = client.get("/native/v1/cultural_survey/questions")

        assert response.status_code == 200
        assert response.json == {
            "questions": [
                {
                    "id": "SORTIES",
                    "title": "Au cours de l'année précédente, tu as/es au moins une fois ...",
                    "answers": [
                        {
                            "id": "FESTIVAL",
                            "title": "Participé à un festival,",
                            "subtitle": "à une avant-première",
                            "sub_question": "FESTIVALS",
                        },
                        {
                            "id": "SPECTACLE",
                            "title": "Assisté à un spectacle",
                            "subtitle": "Pièce de théâtre, cirque, danse...",
                            "sub_question": "SPECTACLES",
                        },
                        {
                            "id": "BIBLIOTHEQUE",
                            "title": "Allé à la bibliothèque",
                            "subtitle": "ou à la médiathèque",
                            "sub_question": None,
                        },
                        {
                            "id": "EVENEMENT_JEU",
                            "title": "Participé à un jeu",
                            "subtitle": "escape game, jeu concours",
                            "sub_question": None,
                        },
                        {"id": "CONCERT", "title": "Allé à un concert", "subtitle": None, "sub_question": None},
                        {"id": "CINEMA", "title": "Allé au cinéma", "subtitle": None, "sub_question": None},
                        {
                            "id": "MUSEE",
                            "title": "Visité un musée,",
                            "subtitle": "un monument, une exposition...",
                            "sub_question": None,
                        },
                        {
                            "id": "CONFERENCE",
                            "title": "Participé à une conférence,",
                            "subtitle": "rencontre ou découverte des métiers de la culture",
                            "sub_question": None,
                        },
                        {
                            "id": "COURS",
                            "title": "Pris un cours",
                            "subtitle": "danse, théâtre, musique, dessin",
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
                    "title": "À quels types de festivals as-tu participé ?",
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
                    "title": "À quels types de spectacles as-tu assisté ?",
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
                    "title": "Au cours de l'année précédente, tu as au moins une fois ...",
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
            ]
        }

    @patch("pcapi.tasks.cultural_survey_tasks.upload_answers_task.delay")
    @freezegun.freeze_time("2020-01-01")
    def test_post_cultural_survey_answers(self, upload_answers_task, client):
        user: users_models.User = users_factories.UserFactory()
        client.with_token(user.email)

        all_answers = [
            {
                "questionId": cultural_survey.SORTIES.id,
                "answerIds": [
                    cultural_survey.FESTIVAL.id,
                ],
            },
            {
                "questionId": cultural_survey.FESTIVALS.id,
                "answerIds": [
                    cultural_survey.FESTIVAL_MUSIQUE.id,
                    cultural_survey.LIVRE.id,
                ],
            },
            {
                "questionId": cultural_survey.ACTIVITES.id,
                "answerIds": [
                    cultural_survey.LIVRE.id,
                    cultural_survey.PODCAST.id,
                ],
            },
        ]
        response = client.post(
            "/native/v1/cultural_survey/answers",
            json={"answers": all_answers},
        )

        assert response.status_code == 204

        expected_answers = [
            {
                "question_id": cultural_survey.SORTIES.id,
                "answer_ids": [
                    cultural_survey.FESTIVAL.id,
                ],
            },
            {
                "question_id": cultural_survey.FESTIVALS.id,
                "answer_ids": [
                    cultural_survey.FESTIVAL_MUSIQUE.id,
                    cultural_survey.LIVRE.id,
                ],
            },
            {
                "question_id": cultural_survey.ACTIVITES.id,
                "answer_ids": [
                    cultural_survey.LIVRE.id,
                    cultural_survey.PODCAST.id,
                ],
            },
        ]
        upload_answers_task.assert_called_once_with(
            serializers.CulturalSurveyAnswersForData(
                user_id=user.id, answers=expected_answers, submitted_at=datetime.datetime.utcnow()
            )
        )
        assert not user.needsToFillCulturalSurvey
        assert user.culturalSurveyFilledDate == datetime.datetime.utcnow()
