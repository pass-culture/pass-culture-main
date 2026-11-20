import typing

from pcapi.core.nature_format_domain.nfd_fields import FieldEnum


# Common fields shared across all offers
COMMON_CAPABILITIES: typing.Final[list[FieldEnum]] = [
    FieldEnum.BOOKING_LIMIT,
    FieldEnum.BOOKING_OPENING_DATE,
    FieldEnum.COMPLEMENTARY_INFO,
    FieldEnum.EMAIL_NOTIFICATION,
    FieldEnum.IMAGE,
    FieldEnum.NO_CREDIT_LINK,
    FieldEnum.PRICE,
    FieldEnum.PROGRAM_PUBLICATION,
]

COMMON_MANDATORY_FIELDS: typing.Final[list[FieldEnum]] = [
    FieldEnum.PRICE,
    FieldEnum.TITLE,
]

# Common fields of Bien
BIEN_CAPABILITIES: typing.Final[list[FieldEnum]] = [
    FieldEnum.ACCESSIBILITY_VENUE,
    FieldEnum.COUNTERMARK,
    FieldEnum.DESCRIPTION,
    FieldEnum.EAN,
    FieldEnum.LOCATION,
    FieldEnum.PICKUP_30_DAYS,
    FieldEnum.STOCK,
    FieldEnum.TITLE_BIEN,
]

BIEN_MANDATORY_FIELDS: typing.Final[list[FieldEnum]] = [
    FieldEnum.LOCATION,
    FieldEnum.PICKUP_30_DAYS,
    FieldEnum.STOCK,
]

# Common fields of Evenement
EVENEMENT_CAPABILITIES: typing.Final[list[FieldEnum]] = [
    FieldEnum.CONTACT_EMAIL,
    FieldEnum.COUNTERMARK,
    FieldEnum.DESCRIPTION,
    FieldEnum.DURATION,
    FieldEnum.DUO_OFFER,
    FieldEnum.IS_MEDIATION,
    FieldEnum.IS_MULTIPRICE,
    FieldEnum.LOCATION,
    FieldEnum.STANDARD_REFUND,
    FieldEnum.START_DATE,
    FieldEnum.TITLE,
    FieldEnum.VIDEO,
    FieldEnum.WITHDRAWAL_TYPES,
]


EVENEMENT_MANDATORY_FIELDS: typing.Final[list[FieldEnum]] = [
    FieldEnum.LOCATION,
    FieldEnum.START_DATE,
]

# Common fields of Carte et Abonnement
CARTE_CAPABILITIES: typing.Final[list[FieldEnum]] = [
    FieldEnum.COUNTERMARK,
    FieldEnum.STOCK,
]

# Domains mapping for field variations
CARTE_NO_REFUND_DOMAINS = {"JEUX_VIDEO", "MEDIA_PRESSE_RADIO_EN_LIGNE", "STREAMING_MUSIQUE", "VOD"}
CARTE_REFUND_DOMAINS = {
    "MUSEE_PATRIMOINE_ARCHITECTURE",
    "ART_VISUEL",
    "BIBLIOTHEQUE_MEDIATHEQUE",
    "CINEMA",
    "COMEDIE_MUSICALE",
    "CIRQUE_ARTS_RUE",
    "CULTURE_SCIENTIFIQUE",
    "DANSE",
    "LITTERATURE",
    "MULTI_DOMAINES_CARTE_JEUNE",
    "MUSIQUE",
    "OPERA",
    "MEDIA_PRESSE_RADIO",
    "STAND_UP",
    "THEATRE",
}

CARTE_MANDATORY_FIELDS: typing.Final[list[FieldEnum]] = [
    FieldEnum.BOOKING_LIMIT,
    FieldEnum.STOCK,
]

# Common fields of Numerique
NUMERIQUE_CAPABILITIES: typing.Final[list[FieldEnum]] = [
    FieldEnum.DESCRIPTION,
    FieldEnum.OFFER_URL,
    FieldEnum.STOCK,
    FieldEnum.TITLE,
]
