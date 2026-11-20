import enum
import typing


class NatureEnum(enum.Enum):
    BIEN = "BIEN"
    CARTE_ABONNEMENT = "CARTE_ABONNEMENT"
    EVENEMENT = "EVENEMENT"
    NUMERIQUE = "NUMERIQUE"


class FormatEnum(enum.Enum):
    ABONNEMENT = "ABONNEMENT"
    ATELIER = "ATELIER"
    CARTE = "CARTE"
    CD = "CD"
    CONCERT = "CONCERT"
    CONFERENCE = "CONFERENCE"
    DVD_BLU_RAY = "DVD_BLU_RAY"
    EVENEMENT_NUMERIQUE = "EVENEMENT_NUMERIQUE"
    FESTIVAL = "FESTIVAL"
    INSTRUMENT_DE_MUSIQUE = "INSTRUMENT_DE_MUSIQUE"
    JEUX_EN_LIGNE = "JEUX_EN_LIGNE"
    LIVRE_PAPIER = "LIVRE_PAPIER"
    LIVRE_NUMERIQUE = "LIVRE_NUMERIQUE"
    MATERIEL_ARTS_CREATIFS = "MATERIEL_ARTS_CREATIFS"
    MEDIA = "MEDIA"
    PODCAST = "PODCAST"
    SALON = "SALON"
    SEANCE_CINEMA = "SEANCE_CINEMA"
    SEANCE_ESSAI = "SEANCE_ESSAI"
    SPECTACLE = "SPECTACLE"
    VISITE_GUIDEE = "VISITE_GUIDEE"
    VINYLE = "VINYLE"
    VISITE_LIBRE = "VISITE_LIBRE"
    VISITE_VIRTUELLE = "VISITE_VIRTUELLE"
    VOD = "VOD"


class DomainEnum(enum.Enum):
    BIBLIOTHEQUE_MEDIATHEQUE = "BIBLIOTHEQUE_MEDIATHEQUE"
    LITTERATURE = "LITTERATURE"
    CINEMA = "CINEMA"
    MUSEE_PATRIMOINE_ARCHITECTURE = "MUSEE_PATRIMOINE_ARCHITECTURE"
    ART_VISUEL = "ART_VISUEL"
    CULTURE_SCIENTIFIQUE = "CULTURE_SCIENTIFIQUE"
    MEDIA_PRESSE_RADIO = "MEDIA_PRESSE_RADIO"
    MUSIQUE = "MUSIQUE"
    MULTI_DOMAINES_CARTE_JEUNE = "MULTI_DOMAINES_CARTE_JEUNE"
    CIRQUE_ARTS_RUE = "CIRQUE_ARTS_RUE"
    COMEDIE_MUSICALE = "COMEDIE_MUSICALE"
    STAND_UP = "STAND_UP"
    DANSE = "DANSE"
    OPERA = "OPERA"
    THEATRE = "THEATRE"
    JEUX_VIDEO = "JEUX_VIDEO"
    SANS_DOMAINE = "SANS_DOMAINE"
    STREAMING_MUSIQUE = "STREAMING_MUSIQUE"
    VOD = "VOD"
    MEDIA_PRESSE_RADIO_EN_LIGNE = "MEDIA_PRESSE_RADIO_EN_LIGNE"


# Média, radio, presse


class FieldEnum(enum.Enum):
    TITLE = "TITLE"
    DESCRIPTION = "DESCRIPTION"
    IMAGE = "IMAGE"
    GENRE_MUSIC = "GENRE_MUSIC"
    PERFORMER = "PERFORMER"
    EAN = "EAN"
    AUTHOR = "AUTHOR"
    ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT = "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"


class DomainLabel(typing.TypedDict):
    domain: DomainEnum
    label: str


DOMAIN_LABELS: typing.Final[dict[DomainEnum, str]] = {
    DomainEnum.BIBLIOTHEQUE_MEDIATHEQUE: "Bibliothèque, Médiathèque",
    DomainEnum.LITTERATURE: "Littérature",
    DomainEnum.CINEMA: "Cinéma",
    DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE: "Musée, Patrimoine, Architecture",
    DomainEnum.ART_VISUEL: "Art visuel",
    DomainEnum.CULTURE_SCIENTIFIQUE: "Culture scientifique",
    DomainEnum.MEDIA_PRESSE_RADIO: "Média, Presse, Radio",
    DomainEnum.MUSIQUE: "Musique",
    DomainEnum.MULTI_DOMAINES_CARTE_JEUNE: "Multi-domaines (carte jeune)",
    DomainEnum.CIRQUE_ARTS_RUE: "Cirque et Arts de la rue",
    DomainEnum.COMEDIE_MUSICALE: "Comédie musicale",
    DomainEnum.STAND_UP: "Stand up",
    DomainEnum.DANSE: "Danse",
    DomainEnum.OPERA: "Opéra",
    DomainEnum.THEATRE: "Théâtre",
    DomainEnum.JEUX_VIDEO: "Jeux vidéo",
    DomainEnum.SANS_DOMAINE: "Sans domaine",
    DomainEnum.STREAMING_MUSIQUE: "Streaming de musique",
    DomainEnum.VOD: "Vidéo à la demande",
    DomainEnum.MEDIA_PRESSE_RADIO_EN_LIGNE: "Média, Presse, Radio en ligne",
}


def _domain_label(domain: DomainEnum) -> DomainLabel:
    return {"domain": domain, "label": DOMAIN_LABELS[domain]}


# Nature Format Domain
NFD = [
    {
        "nature": NatureEnum.BIEN,
        "label": "Bien",
        "formats": [
            {"format": FormatEnum.CD, "label": "CD", "domains": []},
            {"format": FormatEnum.VINYLE, "label": "Vinyle", "domains": []},
            {"format": FormatEnum.DVD_BLU_RAY, "label": "DVD, Blu-ray", "domains": []},
            {"format": FormatEnum.INSTRUMENT_DE_MUSIQUE, "label": "Instrument de musique", "domains": []},
            {"format": FormatEnum.LIVRE_PAPIER, "label": "Livre", "domains": []},
            {"format": FormatEnum.MATERIEL_ARTS_CREATIFS, "label": "Matériel d'art créatif", "domains": []},
        ],
    },
    {
        "nature": NatureEnum.CARTE_ABONNEMENT,
        "label": "Carte ou abonnement",
        "formats": [
            {
                "format": FormatEnum.CARTE,
                "label": "Carte, Pass",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.BIBLIOTHEQUE_MEDIATHEQUE),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO_EN_LIGNE),
                    _domain_label(DomainEnum.MULTI_DOMAINES_CARTE_JEUNE),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.STREAMING_MUSIQUE),
                    _domain_label(DomainEnum.THEATRE),
                    _domain_label(DomainEnum.VOD),
                ],
            },
            {
                "format": FormatEnum.ABONNEMENT,
                "label": "Abonnement",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.BIBLIOTHEQUE_MEDIATHEQUE),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO_EN_LIGNE),
                    _domain_label(DomainEnum.MULTI_DOMAINES_CARTE_JEUNE),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.STREAMING_MUSIQUE),
                    _domain_label(DomainEnum.THEATRE),
                    _domain_label(DomainEnum.VOD),
                ],
            },
        ],
    },
    {
        "nature": NatureEnum.EVENEMENT,
        "label": "Événement",
        "formats": [
            {
                "format": FormatEnum.ATELIER,
                "label": "Atelier, cours, stage",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {"format": FormatEnum.CONCERT, "label": "Concert", "domains": []},
            {
                "format": FormatEnum.CONFERENCE,
                "label": "Conférence, rencontre",
                "domains": [
                    _domain_label(DomainEnum.SANS_DOMAINE),
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {
                "format": FormatEnum.FESTIVAL,
                "label": "Festival",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {
                "format": FormatEnum.SALON,
                "label": "Salon, Convention",
                "domains": [
                    _domain_label(DomainEnum.SANS_DOMAINE),
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {"format": FormatEnum.SEANCE_CINEMA, "label": "Séance de cinéma", "domains": []},
            {
                "format": FormatEnum.SEANCE_ESSAI,
                "label": "Séance d'essai",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {
                "format": FormatEnum.SPECTACLE,
                "label": "Spectacle, Représentation",
                "domains": [
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.COMEDIE_MUSICALE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.STAND_UP),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {
                "format": FormatEnum.VISITE_LIBRE,
                "label": "Visite",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.JEUX_VIDEO),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
            {
                "format": FormatEnum.VISITE_GUIDEE,
                "label": "Visite guidée",
                "domains": [
                    _domain_label(DomainEnum.ART_VISUEL),
                    _domain_label(DomainEnum.CINEMA),
                    _domain_label(DomainEnum.CIRQUE_ARTS_RUE),
                    _domain_label(DomainEnum.CULTURE_SCIENTIFIQUE),
                    _domain_label(DomainEnum.DANSE),
                    _domain_label(DomainEnum.LITTERATURE),
                    _domain_label(DomainEnum.MEDIA_PRESSE_RADIO),
                    _domain_label(DomainEnum.MUSEE_PATRIMOINE_ARCHITECTURE),
                    _domain_label(DomainEnum.MUSIQUE),
                    _domain_label(DomainEnum.OPERA),
                    _domain_label(DomainEnum.THEATRE),
                ],
            },
        ],
    },
    {
        "nature": NatureEnum.NUMERIQUE,
        "label": "Offre numérique",
        "formats": [
            {"format": FormatEnum.VOD, "label": "Vidéo à la demande", "domains": []},
            {"format": FormatEnum.JEUX_EN_LIGNE, "label": "Jeux en ligne", "domains": []},
            {"format": FormatEnum.VISITE_VIRTUELLE, "label": "Visite virtuelle", "domains": []},
            {"format": FormatEnum.PODCAST, "label": "Podcast", "domains": []},
            {"format": FormatEnum.MEDIA, "label": "Média", "domains": []},
            {"format": FormatEnum.LIVRE_NUMERIQUE, "label": "Livre numérique, E-book, Livre audio", "domains": []},
            {"format": FormatEnum.EVENEMENT_NUMERIQUE, "label": "Événement numérique", "domains": []},
        ],
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
