import enum


class NatureEnum(enum.Enum):
    BIEN = "BIEN"
    CARTE_ABONNEMENT = "CARTE_ABONNEMENT"
    EVENEMENT = "EVENEMENT"
    NUMERIQUE = "NUMERIQUE"


class FormatEnum(enum.Enum):
    CD_VINYLE = "CD_VINYLE"
    DVD_BLU_RAY = "DVD_BLU_RAY"
    INSTRUMENT_DE_MUSIQUE = "INSTRUMENT_DE_MUSIQUE"
    LIVRE_PAPIER = "LIVRE_PAPIER"
    MATERIEL_ARTS_CREATIFS = "MATERIEL_ARTS_CREATIFS"


# Nature Format Domain
NFD = [
    {
        "name": NatureEnum.BIEN,
        "label": "Biens",
        "formats": [
            {
                "format": FormatEnum.CD_VINYLE,
                "label": "CD, Vinyle",
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
                "label": "Livre papier",
            },
            {
                "format": FormatEnum.MATERIEL_ARTS_CREATIFS,
                "label": "Matériel arts créatifs",
            },
        ],
    },
    {
        "name": NatureEnum.CARTE_ABONNEMENT,
        "label": "Cartes d'abonnement",
        "formats": [],
    },
    {
        "name": NatureEnum.EVENEMENT,
        "label": "Événements",
        "formats": [],
    },
    {
        "name": NatureEnum.NUMERIQUE,
        "label": "Offre numérique",
        "formats": [],
    },
]


def get_capabilities(nature: NatureEnum, format: FormatEnum) -> list[str]:
    if nature == NatureEnum.BIEN:
        if format == FormatEnum.CD_VINYLE:
            return ["TITLE", "DESCRIPTION", "IMAGE", "GTL_ID", "EAN", "PERFORMER"]
        if format == FormatEnum.DVD_BLU_RAY:
            return ["TITLE", "DESCRIPTION", "IMAGE", "GTL_ID", "EAN"]
        if format == FormatEnum.INSTRUMENT_DE_MUSIQUE:
            return ["TITLE", "DESCRIPTION", "IMAGE", "EAN"]
        if format == FormatEnum.LIVRE_PAPIER:
            return ["TITLE", "DESCRIPTION", "IMAGE", "EAN", "GTL_ID", "AUTHOR", "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"]
        if format == FormatEnum.MATERIEL_ARTS_CREATIFS:
            return ["TITLE", "DESCRIPTION", "IMAGE", "EAN"]
    return []
