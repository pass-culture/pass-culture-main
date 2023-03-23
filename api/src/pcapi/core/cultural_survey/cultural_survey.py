from dataclasses import dataclass

from pcapi.core.cultural_survey.models import CulturalSurveyAnswerEnum
from pcapi.core.cultural_survey.models import CulturalSurveyQuestionEnum


@dataclass()
class CulturalSurveyAnswer:
    id: CulturalSurveyAnswerEnum
    title: str
    subtitle: str | None = None
    sub_question: CulturalSurveyQuestionEnum | None = None


@dataclass()
class CulturalSurveyQuestion:
    id: CulturalSurveyQuestionEnum
    title: str
    answers: list[CulturalSurveyAnswer]


FESTIVAL = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL,
    title="À un festival",
    sub_question=CulturalSurveyQuestionEnum.FESTIVALS,
)
SPECTACLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE,
    title="À un spectacle",
    subtitle="(pièce de théâtre, cirque, danse...)",
    sub_question=CulturalSurveyQuestionEnum.SPECTACLES,
)
BIBLIOTHEQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.BIBLIOTHEQUE,
    title="À la bibliothèque",
    subtitle="ou à la médiathèque",
)
EVENEMENT_JEU = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.EVENEMENT_JEU,
    title="À un escape game",
    subtitle="ou participé à un jeu, jeu concours",
)
CONCERT = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CONCERT,
    title="À un concert",
)
CINEMA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CINEMA,
    title="Au cinéma",
)
MUSEE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.MUSEE,
    title="Au musée,",
    subtitle="un monument, une exposition...",
)
CONFERENCE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.CONFERENCE,
    title="À une conférence,",
    subtitle="une rencontre ou une découverte des métiers de la Culture",
)
COURS = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.COURS,
    title="À un cours",
    subtitle="(danse, théâtre, musique, dessin...)",
)
SANS_SORTIES = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SANS_SORTIES,
    title="Aucune de ces sorties culturelles",
)

FESTIVAL_MUSIQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_MUSIQUE,
    title="Festival de musique",
)
FESTIVAL_AVANT_PREMIERE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_AVANT_PREMIERE,
    title="Avant-première de film",
)
FESTIVAL_SPECTACLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_SPECTACLE,
    title="Festival de danse, de cirque",
)
FESTIVAL_LIVRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_LIVRE,
    title="Festival littéraire",
)
FESTIVAL_CINEMA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_CINEMA,
    title="Festival de cinéma",
)
FESTIVAL_AUTRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FESTIVAL_AUTRE,
    title="Autre festival",
)

SPECTACLE_HUMOUR = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_HUMOUR,
    title="Spectacle d'humour",
    subtitle="ou café-théâtre",
)
SPECTACLE_THEATRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_THEATRE,
    title="Théâtre",
)
SPECTACLE_RUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_RUE,
    title="Spectacle de rue",
)
SPECTACLE_OPERA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_OPERA,
    title="Comédie musicale, opéra",
)
SPECTACLE_CIRQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_CIRQUE,
    title="Cirque",
)
SPECTACLE_DANSE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_DANSE,
    title="Spectacle de danse",
)
SPECTACLE_AUTRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SPECTACLE_AUTRE,
    title="Autres spectacles",
)

MATERIEL_ART_CREATIF = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.MATERIEL_ART_CREATIF,
    title="Utilisé du matériel d'art",
    subtitle="pour peindre, dessiner...",
)
PODCAST = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PODCAST,
    title="Écouté un podcast",
)
LIVRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.LIVRE,
    title="Lu un livre",
)
JOUE_INSTRUMENT = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.JOUE_INSTRUMENT,
    title="Joué d'un instrument de musique ",
)
PRESSE_EN_LIGNE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PRESSE_EN_LIGNE,
    title="Lu un article de presse",
    subtitle="en ligne",
)
JEU_VIDEO = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.JEU_VIDEO,
    title="Joué à un jeu vidéo",
)
FILM_DOMICILE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.FILM_DOMICILE,
    title="Regardé un film chez toi",
)
SANS_ACTIVITES = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.SANS_ACTIVITES,
    title="Aucune de ces activités culturelles",
)

PROJECTION_FESTIVAL = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_FESTIVAL,
    title="Aller à un festival",
    subtitle="Musique, cinéma, littéraire, ...",
)


PROJECTION_CINEMA = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_CINEMA,
    title="Aller au cinéma",
)

PROJECTION_VISITE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_VISITE,
    title="Faire des visites",
    subtitle="Une exposition, un monument, ...",
)

PROJECTION_CONCERT = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_CONCERT,
    title="Participer à un concert",
)


PROJECTION_CD_VINYLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_CD_VINYLE,
    title="Écouter des CDs ou des vinyls",
)


PROJECTION_SPECTACLE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_SPECTACLE,
    title="Voir un spectacle",
    subtitle="Pièce de théâtre, cirque, humour, ...",
)


PROJECTION_ACTIVITE_ARTISTIQUE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_ACTIVITE_ARTISTIQUE,
    title="Faire une activité artistique",
    subtitle="Dessin, danse, théâtre, musique, ...",
)


PROJECTION_LIVRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_LIVRE,
    title="Lire des livres",
)


PROJECTION_CONFERENCE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_CONFERENCE,
    title="Assister à des conférences ou des rencontres",
)

PROJECTION_JEU = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_JEU,
    title="Faire des jeux en solo ou en duo",
    subtitle="Escape games, jeux vidéo, ...",
)

PROJECTION_AUTRE = CulturalSurveyAnswer(
    id=CulturalSurveyAnswerEnum.PROJECTION_AUTRE,
    title="Autre",
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
PROJECTION_ANSWERS = [
    PROJECTION_FESTIVAL,
    PROJECTION_CINEMA,
    PROJECTION_VISITE,
    PROJECTION_CONCERT,
    PROJECTION_CD_VINYLE,
    PROJECTION_SPECTACLE,
    PROJECTION_ACTIVITE_ARTISTIQUE,
    PROJECTION_LIVRE,
    PROJECTION_CONFERENCE,
    PROJECTION_JEU,
    PROJECTION_AUTRE,
]


SORTIES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.SORTIES,
    title="Au cours de l'année précédente, tu as été au moins une fois ...",
    answers=SORTIES_ANSWERS,
)

FESTIVALS = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.FESTIVALS,
    title="À quels types de festivals as-tu participé ?",
    answers=FESTIVALS_ANSWERS,
)

SPECTACLES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.SPECTACLES,
    title="À quels types de spectacles as-tu assisté ?",
    answers=SPECTACLES_ANSWERS,
)

ACTIVITES = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.ACTIVITES,
    title="Au cours de l'année précédente, tu as au moins une fois ...",
    answers=ACTIVITES_ANSWERS,
)

PROJECTIONS = CulturalSurveyQuestion(
    id=CulturalSurveyQuestionEnum.PROJECTIONS,
    title="Cette année, tu aimerais ...",
    answers=PROJECTION_ANSWERS,
)

ALL_CULTURAL_SURVEY_QUESTIONS = [
    SORTIES,
    FESTIVALS,
    SPECTACLES,
    ACTIVITES,
    PROJECTIONS,
]
