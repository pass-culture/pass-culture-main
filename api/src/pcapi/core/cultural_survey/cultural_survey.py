from dataclasses import dataclass
from typing import Optional

from pcapi.core.cultural_survey.models import CulturalSurveyAnswerEnum
from pcapi.core.cultural_survey.models import CulturalSurveyQuestionEnum


@dataclass()
class CulturalSurveyAnswer:
    id: CulturalSurveyAnswerEnum
    title: str
    subtitle: Optional[str] = None
    sub_question: Optional[CulturalSurveyQuestionEnum] = None


@dataclass()
class CulturalSurveyQuestion:
    id: CulturalSurveyQuestionEnum
    title: str
    answers: list[CulturalSurveyAnswer]


FESTIVAL = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL.value,
    title="Participé à un festival,",
    subtitle="à une avant-première",
    sub_question=CulturalSurveyQuestionEnum.FESTIVALS,
)
SPECTACLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE.value,
    title="Assisté à un spectacle",
    subtitle="Pièce de théâtre, cirque, danse...",
    sub_question=CulturalSurveyQuestionEnum.SPECTACLES,
)
BIBLIOTHEQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.BIBLIOTHEQUE.value,
    title="Allé à la bibliothèque",
    subtitle="ou à la médiathèque",
)
EVENEMENT_JEU = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.EVENEMENT_JEU.value,
    title="Participé à un jeu",
    subtitle="escape game, jeu concours",
)
CONCERT = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CONCERT.value,
    title="Allé à un concert",
)
CINEMA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CINEMA.value,
    title="Allé au cinéma",
)
MUSEE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.MUSEE.value,
    title="Visité un musée,",
    subtitle="un monument, une exposition...",
)
CONFERENCE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CONFERENCE.value,
    title="Participé à une conférence,",
    subtitle="rencontre ou découverte des métiers de la culture",
)
COURS = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.COURS.value,
    title="Pris un cours",
    subtitle="danse, théâtre, musique, dessin",
)
SANS_SORTIES = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SANS_SORTIES.value,
    title="Aucune de ces sorties culturelles",
)

FESTIVAL_MUSIQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_MUSIQUE.value,
    title="Festival de musique",
)
FESTIVAL_AVANT_PREMIERE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_AVANT_PREMIERE.value,
    title="Avant-première de film",
)
FESTIVAL_SPECTACLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_SPECTACLE.value,
    title="Festival de danse, de cirque",
)
FESTIVAL_LIVRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_LIVRE.value,
    title="Festival littéraire",
)
FESTIVAL_CINEMA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_CINEMA.value,
    title="Festival de cinéma",
)
FESTIVAL_AUTRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_AUTRE.value,
    title="Autre festival",
)

SPECTACLE_HUMOUR = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_HUMOUR.value,
    title="Spectacle d'humour",
    subtitle="ou café-théâtre",
)
SPECTACLE_THEATRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_THEATRE.value,
    title="Théâtre",
)
SPECTACLE_RUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_RUE.value,
    title="Spectacle de rue",
)
SPECTACLE_OPERA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_OPERA.value,
    title="Comédie musicale, opéra",
)
SPECTACLE_CIRQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_CIRQUE.value,
    title="Cirque",
)
SPECTACLE_DANSE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_DANSE.value,
    title="Spectacle de danse",
)
SPECTACLE_AUTRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_AUTRE.value,
    title="Autres spectacles",
)

MATERIEL_ART_CREATIF = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.MATERIEL_ART_CREATIF.value,
    title="Utilisé du matériel d'art",
    subtitle="pour peindre, dessiner...",
)
PODCAST = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PODCAST.value,
    title="Écouté un podcast",
)
LIVRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.LIVRE.value,
    title="Lu un livre",
)
JOUE_INSTRUMENT = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.JOUE_INSTRUMENT.value,
    title="Joué d'un instrument de musique ",
)
PRESSE_EN_LIGNE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PRESSE_EN_LIGNE.value,
    title="Lu un article de presse",
    subtitle="en ligne",
)
JEU_VIDEO = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.JEU_VIDEO.value,
    title="Joué à un jeu vidéo",
)
FILM_DOMICILE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FILM_DOMICILE.value,
    title="Regardé un film chez toi",
)
SANS_ACTIVITES = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SANS_ACTIVITES.value,
    title="Aucune de ces activités culturelles",
)

ALL_CULTURAL_SURVEY_ANSWERS = (
    FESTIVAL,
    SPECTACLE,
    BIBLIOTHEQUE,
    EVENEMENT_JEU,
    CONCERT,
    CINEMA,
    MUSEE,
    CONFERENCE,
    COURS,
    SANS_SORTIES,
    FESTIVAL_MUSIQUE,
    FESTIVAL_AVANT_PREMIERE,
    FESTIVAL_SPECTACLE,
    FESTIVAL_LIVRE,
    FESTIVAL_CINEMA,
    FESTIVAL_AUTRE,
    SPECTACLE_HUMOUR,
    SPECTACLE_THEATRE,
    SPECTACLE_RUE,
    SPECTACLE_OPERA,
    SPECTACLE_CIRQUE,
    SPECTACLE_DANSE,
    SPECTACLE_AUTRE,
    MATERIEL_ART_CREATIF,
    PODCAST,
    LIVRE,
    JOUE_INSTRUMENT,
    PRESSE_EN_LIGNE,
    JEU_VIDEO,
    FILM_DOMICILE,
    SANS_ACTIVITES,
)


CulturalSurveyAnswersDict = {answer.id: answer for answer in ALL_CULTURAL_SURVEY_ANSWERS}


SORTIES_ANSWERS = [
    FESTIVAL,
    SPECTACLE,
    BIBLIOTHEQUE,
    EVENEMENT_JEU,
    CONCERT,
    CINEMA,
    MUSEE,
    CONFERENCE,
    COURS,
    SANS_SORTIES,
]
FESTIVALS_ANSWERS = [
    FESTIVAL_MUSIQUE,
    FESTIVAL_AVANT_PREMIERE,
    FESTIVAL_SPECTACLE,
    FESTIVAL_LIVRE,
    FESTIVAL_CINEMA,
    FESTIVAL_AUTRE,
]
SPECTACLES_ANSWERS = [
    SPECTACLE_HUMOUR,
    SPECTACLE_THEATRE,
    SPECTACLE_RUE,
    SPECTACLE_OPERA,
    SPECTACLE_CIRQUE,
    SPECTACLE_DANSE,
    SPECTACLE_AUTRE,
]
ACTIVITES_ANSWERS = [
    MATERIEL_ART_CREATIF,
    PODCAST,
    LIVRE,
    JOUE_INSTRUMENT,
    PRESSE_EN_LIGNE,
    JEU_VIDEO,
    FILM_DOMICILE,
    SANS_ACTIVITES,
]


SORTIES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.SORTIES.value,
    title="Au cours de l'année précédente, tu as/es au moins une fois ...",
    answers=SORTIES_ANSWERS,
)

FESTIVALS = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.FESTIVALS.value,
    title="À quels types de festivals as-tu participé ?",
    answers=FESTIVALS_ANSWERS,
)

SPECTACLES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.SPECTACLES.value,
    title="À quels types de spectacles as-tu assisté ?",
    answers=SPECTACLES_ANSWERS,
)

ACTIVITES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.ACTIVITES.value,
    title="Au cours de l'année précédente, tu as au moins une fois ...",
    answers=ACTIVITES_ANSWERS,
)

ALL_CULTURAL_SURVEY_QUESTIONS = [
    SORTIES,
    FESTIVALS,
    SPECTACLES,
    ACTIVITES,
]
