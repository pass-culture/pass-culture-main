from dataclasses import dataclass
from typing import Optional

from pcapi.core.cultural_survey.models import CulturalSurveyQuestionEnum


@dataclass()
class CulturalSurveyAnswer:
    id: str
    title: str
    subtitle: Optional[str] = None
    sub_question: Optional[CulturalSurveyQuestionEnum] = None


@dataclass()
class CulturalSurveyQuestion:
    id: str
    title: str
    answers: list[CulturalSurveyAnswer]


FESTIVAL = CulturalSurveyAnswer(
    id="FESTIVAL",
    title="Participé à un festival,",
    subtitle="à une avant-première",
    sub_question=CulturalSurveyQuestionEnum.FESTIVALS,
)
SPECTACLE = CulturalSurveyAnswer(
    id="SPECTACLE",
    title="Assisté à un spectacle",
    subtitle="Pièce de théâtre, cirque, danse...",
    sub_question=CulturalSurveyQuestionEnum.SPECTACLES,
)
BIBLIOTHEQUE = CulturalSurveyAnswer(
    id="BIBLIOTHEQUE",
    title="Allé à la bibliothèque",
    subtitle="ou à la médiathèque",
)
EVENEMENT_JEU = CulturalSurveyAnswer(
    id="EVENEMENT_JEU",
    title="Participé à un jeu",
    subtitle="escape game, jeu concours",
)
CONCERT = CulturalSurveyAnswer(
    id="CONCERT",
    title="Allé à un concert",
)
CINEMA = CulturalSurveyAnswer(
    id="CINEMA",
    title="Allé au cinéma",
)
MUSEE = CulturalSurveyAnswer(
    id="MUSEE",
    title="Visité un musée,",
    subtitle="un monument, une exposition...",
)
CONFERENCE = CulturalSurveyAnswer(
    id="CONFERENCE",
    title="Participé à une conférence,",
    subtitle="rencontre ou découverte des métiers de la culture",
)
COURS = CulturalSurveyAnswer(
    id="COURS",
    title="Pris un cours",
    subtitle="danse, théâtre, musique, dessin",
)
SANS_SORTIES = CulturalSurveyAnswer(
    id="SANS_SORTIES",
    title="Aucune de ces sorties culturelles",
)

FESTIVAL_MUSIQUE = CulturalSurveyAnswer(
    id="FESTIVAL_MUSIQUE",
    title="Festival de musique",
)
FESTIVAL_AVANT_PREMIERE = CulturalSurveyAnswer(
    id="FESTIVAL_AVANT_PREMIERE",
    title="Avant-première de film",
)
FESTIVAL_SPECTACLE = CulturalSurveyAnswer(
    id="FESTIVAL_SPECTACLE",
    title="Festival de danse, de cirque",
)
FESTIVAL_LIVRE = CulturalSurveyAnswer(
    id="FESTIVAL_LIVRE",
    title="Festival littéraire",
)
FESTIVAL_CINEMA = CulturalSurveyAnswer(
    id="FESTIVAL_CINEMA",
    title="Festival de cinéma",
)
FESTIVAL_AUTRE = CulturalSurveyAnswer(
    id="FESTIVAL_AUTRE",
    title="Autre festival",
)

SPECTACLE_HUMOUR = CulturalSurveyAnswer(
    id="SPECTACLE_HUMOUR",
    title="Spectacle d'humour",
    subtitle="ou café-théâtre",
)
SPECTACLE_THEATRE = CulturalSurveyAnswer(
    id="SPECTACLE_THEATRE",
    title="Théâtre",
)
SPECTACLE_RUE = CulturalSurveyAnswer(
    id="SPECTACLE_RUE",
    title="Spectacle de rue",
)
SPECTACLE_OPERA = CulturalSurveyAnswer(
    id="SPECTACLE_OPERA",
    title="Comédie musicale, opéra",
)
SPECTACLE_CIRQUE = CulturalSurveyAnswer(
    id="SPECTACLE_CIRQUE",
    title="Cirque",
)
SPECTACLE_DANSE = CulturalSurveyAnswer(
    id="SPECTACLE_DANSE",
    title="Spectacle de danse",
)
SPECTACLE_AUTRE = CulturalSurveyAnswer(
    id="SPECTACLE_AUTRE",
    title="Autres spectacles",
)

MATERIEL_ART_CREATIF = CulturalSurveyAnswer(
    id="MATERIEL_ART_CREATIF",
    title="Utilisé du matériel d'art",
    subtitle="pour peindre, dessiner...",
)
PODCAST = CulturalSurveyAnswer(
    id="PODCAST",
    title="Écouté un podcast",
)
LIVRE = CulturalSurveyAnswer(
    id="LIVRE",
    title="Lu un livre",
)
JOUE_INSTRUMENT = CulturalSurveyAnswer(
    id="JOUE_INSTRUMENT",
    title="Joué d'un instrument de musique ",
)
PRESSE_EN_LIGNE = CulturalSurveyAnswer(
    id="PRESSE_EN_LIGNE",
    title="Lu un article de presse",
    subtitle="en ligne",
)
JEU_VIDEO = CulturalSurveyAnswer(
    id="JEU_VIDEO",
    title="Joué à un jeu vidéo",
)
FILM_DOMICILE = CulturalSurveyAnswer(
    id="FILM_DOMICILE",
    title="Regardé un film chez toi",
)
SANS_ACTIVITES = CulturalSurveyAnswer(
    id="SANS_ACTIVITES",
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
