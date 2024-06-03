from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Category:
    id: str
    pro_label: str
    is_selectable: bool = True


# region Categories declarations

BEAUX_ARTS = Category(
    id="BEAUX_ARTS",
    pro_label="Beaux-arts",
)
CARTE_JEUNES = Category(
    id="CARTE_JEUNES",
    pro_label="Carte jeunes",
)
CINEMA = Category(
    id="CINEMA",
    pro_label="Cinéma",
)
CONFERENCE_RENCONTRE = Category(
    id="CONFERENCE",
    pro_label="Conférences, rencontres",
)
FILM = Category(
    id="FILM",
    pro_label="Films, vidéos",
)
INSTRUMENT = Category(
    id="INSTRUMENT",
    pro_label="Instrument de musique",
)
JEU = Category(
    id="JEU",
    pro_label="Jeux",
)
LIVRE = Category(
    id="LIVRE",
    pro_label="Livre",
)
MEDIA = Category(
    id="MEDIA",
    pro_label="Médias",
)
MUSEE = Category(
    id="MUSEE",
    pro_label="Musée, patrimoine, architecture, arts visuels",
)
MUSIQUE_ENREGISTREE = Category(
    id="MUSIQUE_ENREGISTREE",
    pro_label="Musique enregistrée",
)
MUSIQUE_LIVE = Category(
    id="MUSIQUE_LIVE",
    pro_label="Musique live",
)
PRATIQUE_ART = Category(
    id="PRATIQUE_ART",
    pro_label="Pratique artistique",
)
SPECTACLE = Category(
    id="SPECTACLE",
    pro_label="Spectacle vivant",
)
TECHNIQUE = Category(
    id="TECHNIQUE",
    pro_label="Catégorie technique",
    is_selectable=False,
)
# endregion

ALL_CATEGORIES = (
    BEAUX_ARTS,
    CARTE_JEUNES,
    CINEMA,
    CONFERENCE_RENCONTRE,
    FILM,
    INSTRUMENT,
    JEU,
    LIVRE,
    MEDIA,
    MUSEE,
    MUSIQUE_ENREGISTREE,
    MUSIQUE_LIVE,
    PRATIQUE_ART,
    SPECTACLE,
    TECHNIQUE,
)
ALL_CATEGORIES_DICT = {category.id: category for category in ALL_CATEGORIES}
CategoryIdEnum = Enum("CategoryIdEnum", {category.id: category.id for category in ALL_CATEGORIES})  # type: ignore[misc]
CategoryIdLabelEnum = Enum("CategoryIdLabelEnum", {category.id: category.pro_label for category in ALL_CATEGORIES})  # type: ignore[misc]

assert set(ALL_CATEGORIES) == set(category for category in locals().values() if isinstance(category, Category))


@dataclass
class TiteliveMusicType:
    gtl_id: str
    label: str
    can_be_event: bool = True


TITELIVE_MUSIC_TYPES = (
    TiteliveMusicType(gtl_id="01000000", label="Musique Classique"),
    TiteliveMusicType(gtl_id="02000000", label="Jazz / Blues"),
    TiteliveMusicType(gtl_id="03000000", label="Bandes originales", can_be_event=False),
    TiteliveMusicType(gtl_id="04000000", label="Electro"),
    TiteliveMusicType(gtl_id="05000000", label="Pop"),
    TiteliveMusicType(gtl_id="06000000", label="Rock"),
    TiteliveMusicType(gtl_id="07000000", label="Metal"),
    TiteliveMusicType(gtl_id="08000000", label="Alternatif"),
    TiteliveMusicType(gtl_id="09000000", label="Variétés"),
    TiteliveMusicType(gtl_id="10000000", label="Funk / Soul / RnB / Disco"),
    TiteliveMusicType(gtl_id="11000000", label="Rap/ Hip Hop"),
    TiteliveMusicType(gtl_id="12000000", label="Reggae / Ragga"),
    TiteliveMusicType(gtl_id="13000000", label="Musique du monde"),
    TiteliveMusicType(gtl_id="14000000", label="Country / Folk"),
    TiteliveMusicType(gtl_id="15000000", label="Vidéos musicales", can_be_event=False),
    TiteliveMusicType(gtl_id="16000000", label="Compilations", can_be_event=False),
    TiteliveMusicType(gtl_id="17000000", label="Ambiance"),
    TiteliveMusicType(gtl_id="18000000", label="Enfants", can_be_event=False),
    TiteliveMusicType(gtl_id="19000000", label="Autre"),
)
