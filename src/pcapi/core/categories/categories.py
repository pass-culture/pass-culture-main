from dataclasses import dataclass


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
CINEMA = Category(
    id="CINEMA",
    pro_label="Cinéma",
)
CONFERENCE_RENCONTRE = Category(
    id="CONFERENCE",
    pro_label="Conférences, rencontres, découverte des métiers",
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
    pro_label="Musée, patrimoine, architecture, arts visuels ou contemporains",
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

assert set(ALL_CATEGORIES) == set(category for category in locals().values() if isinstance(category, Category))
