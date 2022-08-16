import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.core.cultural_survey.models import CulturalSurveyAnswerEnum
from pcapi.core.cultural_survey.models import CulturalSurveyQuestionEnum
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


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
                    "title": "Au cours de l'année précédente, tu es allé au moins une fois ...",
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

    @freezegun.freeze_time("2020-01-01")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_post_cultural_survey_answers(self, store_public_object, client):
        user: users_models.User = users_factories.UserFactory()
        client.with_token(user.email)

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
        ]
        response = client.post(
            "/native/v1/cultural_survey/answers",
            json={"answers": all_answers},
        )

        assert response.status_code == 204

        answers_str = (
            '{"user_id": %s, "submitted_at": "2020-01-01T00:00:00", "answers": '
            '[{"question_id": "SORTIES", "answer_ids": ["FESTIVAL"]}, '
            '{"question_id": "FESTIVALS", "answer_ids": ["FESTIVAL_MUSIQUE"]}]}'
        ) % user.id

        # Note: if the path does not exist, GCP creates the necessary folders
        store_public_object.assert_called_once_with(
            folder="QPI_exports/qpi_answers_20200101",
            object_id=f"user_id_{user.id}.jsonl",
            blob=bytes(answers_str, "utf-8"),
            content_type="application/json",
        )

        assert not user.needsToFillCulturalSurvey
        assert user.culturalSurveyFilledDate == datetime.datetime.utcnow()
