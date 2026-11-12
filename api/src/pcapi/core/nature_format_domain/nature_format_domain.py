import enum
import typing


class NatureEnum(enum.Enum):
    BIEN = "BIEN"
    CARTE_ABONNEMENT = "CARTE_ABONNEMENT"
    EVENEMENT = "EVENEMENT"
    NUMERIQUE = "NUMERIQUE"


class FormatEnum(enum.Enum):
    CD = "CD"
    VINYLE = "VINYLE"
    DVD_BLU_RAY = "DVD_BLU_RAY"
    INSTRUMENT_DE_MUSIQUE = "INSTRUMENT_DE_MUSIQUE"
    LIVRE_PAPIER = "LIVRE_PAPIER"
    MATERIEL_ARTS_CREATIFS = "MATERIEL_ARTS_CREATIFS"


class FieldEnum(enum.Enum):
    TITLE = "TITLE"
    DESCRIPTION = "DESCRIPTION"
    IMAGE = "IMAGE"
    GENRE_MUSIC = "GENRE_MUSIC"
    PERFORMER = "PERFORMER"
    EAN = "EAN"
    AUTHOR = "AUTHOR"
    ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT = "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"


# Nature Format Domain
NFD = [
    {
        "name": NatureEnum.BIEN,
        "label": "Bien",
        "formats": [
            {
                "format": FormatEnum.CD,
                "label": "CD",
            },
            {
                "format": FormatEnum.VINYLE,
                "label": "Vinyle",
            },
            {
                "format": FormatEnum.DVD_BLU_RAY,
                "label": "DVD, Blu-ray",
            },
            {
                "format": FormatEnum.INSTRUMENT_DE_MUSIQUE,
                "label": "Instrument de musique",
            },
            {
                "format": FormatEnum.LIVRE_PAPIER,
                "label": "Livre",
            },
            {
                "format": FormatEnum.MATERIEL_ARTS_CREATIFS,
                "label": "Matériel d'art créatif",
            },
        ],
    },
    {
        "name": NatureEnum.CARTE_ABONNEMENT,
        "label": "Carte ou abonnement",
        "formats": [],
    },
    {
        "name": NatureEnum.EVENEMENT,
        "label": "Événement",
        "formats": [],
    },
    {
        "name": NatureEnum.NUMERIQUE,
        "label": "Offre numérique",
        "formats": [],
    },
]


class FormatFields(typing.TypedDict):
    capabilities: list[FieldEnum]
    mandatory_fields: list[FieldEnum]


FIELDS_BIEN: typing.Final[dict[FormatEnum, FormatFields]] = {
    FormatEnum.CD: {
        "capabilities": [
            FieldEnum.TITLE,
            FieldEnum.DESCRIPTION,
            FieldEnum.IMAGE,
            FieldEnum.GENRE_MUSIC,
            FieldEnum.PERFORMER,
            FieldEnum.EAN,
        ],
        "mandatory_fields": [FieldEnum.TITLE, FieldEnum.GENRE_MUSIC],
    },
    FormatEnum.VINYLE: {
        "capabilities": [
            FieldEnum.TITLE,
            FieldEnum.DESCRIPTION,
            FieldEnum.IMAGE,
            FieldEnum.GENRE_MUSIC,
            FieldEnum.PERFORMER,
            FieldEnum.EAN,
        ],
        "mandatory_fields": [FieldEnum.TITLE, FieldEnum.GENRE_MUSIC],
    },
    FormatEnum.DVD_BLU_RAY: {
        "capabilities": [FieldEnum.TITLE, FieldEnum.DESCRIPTION, FieldEnum.IMAGE, FieldEnum.EAN],
        "mandatory_fields": [FieldEnum.TITLE],
    },
    FormatEnum.INSTRUMENT_DE_MUSIQUE: {
        "capabilities": [FieldEnum.TITLE, FieldEnum.DESCRIPTION, FieldEnum.IMAGE, FieldEnum.EAN],
        "mandatory_fields": [FieldEnum.TITLE],
    },
    FormatEnum.LIVRE_PAPIER: {
        "capabilities": [
            FieldEnum.TITLE,
            FieldEnum.DESCRIPTION,
            FieldEnum.IMAGE,
            FieldEnum.EAN,
            FieldEnum.AUTHOR,
            FieldEnum.ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT,
        ],
        "mandatory_fields": [FieldEnum.TITLE],
    },
    FormatEnum.MATERIEL_ARTS_CREATIFS: {
        "capabilities": [FieldEnum.TITLE, FieldEnum.DESCRIPTION, FieldEnum.IMAGE, FieldEnum.EAN],
        "mandatory_fields": [FieldEnum.TITLE],
    },
}


def get_capabilities(nature: NatureEnum, format: FormatEnum) -> list[FieldEnum]:
    if nature == NatureEnum.BIEN:
        return FIELDS_BIEN[format]["capabilities"]
    return []


def get_mandatory_fields(nature: NatureEnum, format: FormatEnum) -> list[FieldEnum]:
    if nature == NatureEnum.BIEN:
        return FIELDS_BIEN[format]["mandatory_fields"]
    return []
