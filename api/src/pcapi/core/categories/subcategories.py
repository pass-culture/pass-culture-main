"""
Old subcategories module.

Do not update a subcategory field here, use the subcategories_v2 module
instead. Unless a field needs to have two different values: in this
case, set the new values in the new module and override it here.
"""
from enum import Enum

from pcapi.core.categories import subcategories_v2


class OnlineOfflinePlatformChoices(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ONLINE_OR_OFFLINE = "ONLINE_OR_OFFLINE"


class SearchGroups(Enum):
    FILM = "Films, séries"
    CINEMA = "Cinéma"
    CONFERENCE = "Conférences, rencontres"
    JEU = "Jeux"
    LIVRE = "Livres"
    VISITE = "Visites, expositions"
    MUSIQUE = "Musique"
    COURS = "Cours, ateliers"
    PRESSE = "Presse, médias"
    SPECTACLE = "Spectacles"
    INSTRUMENT = "Instruments de musique"
    MATERIEL = "Beaux-Arts"
    CARTE_JEUNES = "Carte jeunes"
    NONE = None


class HomepageLabels(Enum):
    FILM = "Films"
    CINEMA = "Cinéma"
    CONFERENCE = "Rencontres"
    JEU = "Jeux"
    LIVRE = "Livres"
    VISITE = "Visites"
    MUSIQUE = "Musique"
    COURS = "Cours"
    PRESSE = "Médias"
    SPECTACLE = "Spectacles"
    INSTRUMENT = "Musique"
    MATERIEL = "Beaux-Arts"
    CARTE_JEUNES = "Carte jeunes"
    NONE = None


class ReimbursementRuleChoices(Enum):
    STANDARD = "STANDARD"
    NOT_REIMBURSED = "NOT_REIMBURSED"
    BOOK = "BOOK"


class Subcategory(subcategories_v2.Subcategory):
    def __post_init__(self) -> None:
        """
        Override references to the subcategories_v2 module's classes.
        """
        if self.search_group_name not in [s.name for s in SearchGroups]:
            raise ValueError("search_group_name can only be one of SearchGroups")
        if self.homepage_label_name not in [h.name for h in HomepageLabels]:
            raise ValueError("search_group_name can only be one of HomepageLabels")
        if self.online_offline_platform not in [o.value for o in OnlineOfflinePlatformChoices]:
            raise ValueError("online_offline_platform can only be one of OnlineOfflinePlatformChoices")
        if self.reimbursement_rule not in [r.value for r in ReimbursementRuleChoices]:
            raise ValueError("online_offline_platform can only be one of ReimbursementRuleChoices")

    @classmethod
    def from_new(cls, base: subcategories_v2.Subcategory, updated_fields: dict) -> "Subcategory":
        base_fields = base.__dict__
        kwargs = base_fields | updated_fields
        return cls(**kwargs)


# region Subcategories declarations
# region FILM
SUPPORT_PHYSIQUE_FILM = Subcategory.from_new(
    subcategories_v2.SUPPORT_PHYSIQUE_FILM,
    {
        "search_group_name": SearchGroups.FILM.name,
        "homepage_label_name": HomepageLabels.FILM.name,
    },
)
ABO_MEDIATHEQUE = Subcategory.from_new(
    subcategories_v2.ABO_MEDIATHEQUE,
    {
        "search_group_name": SearchGroups.FILM.name,
        "homepage_label_name": HomepageLabels.FILM.name,
    },
)
VOD = Subcategory.from_new(
    subcategories_v2.VOD,
    {
        "search_group_name": SearchGroups.FILM.name,
        "homepage_label_name": HomepageLabels.FILM.name,
    },
)
ABO_PLATEFORME_VIDEO = Subcategory.from_new(
    subcategories_v2.ABO_PLATEFORME_VIDEO,
    {
        "search_group_name": SearchGroups.FILM.name,
        "homepage_label_name": HomepageLabels.FILM.name,
    },
)
AUTRE_SUPPORT_NUMERIQUE = Subcategory.from_new(
    subcategories_v2.AUTRE_SUPPORT_NUMERIQUE,
    {
        "search_group_name": SearchGroups.FILM.name,
        "homepage_label_name": HomepageLabels.FILM.name,
    },
)
# endregion
# region CINEMA
CARTE_CINE_MULTISEANCES = Subcategory.from_new(
    subcategories_v2.CARTE_CINE_MULTISEANCES,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
CARTE_CINE_ILLIMITE = Subcategory.from_new(
    subcategories_v2.CARTE_CINE_ILLIMITE,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
SEANCE_CINE = Subcategory.from_new(
    subcategories_v2.SEANCE_CINE,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
EVENEMENT_CINE = Subcategory.from_new(
    subcategories_v2.EVENEMENT_CINE,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
FESTIVAL_CINE = Subcategory.from_new(
    subcategories_v2.FESTIVAL_CINE,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
CINE_VENTE_DISTANCE = Subcategory.from_new(
    subcategories_v2.CINE_VENTE_DISTANCE,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)
CINE_PLEIN_AIR = Subcategory.from_new(
    subcategories_v2.CINE_PLEIN_AIR,
    {
        "search_group_name": SearchGroups.CINEMA.name,
        "homepage_label_name": HomepageLabels.CINEMA.name,
    },
)

# endregion
# region CONFERENCE

CONFERENCE = Subcategory.from_new(
    subcategories_v2.CONFERENCE,
    {
        "search_group_name": SearchGroups.CONFERENCE.name,
        "homepage_label_name": HomepageLabels.CONFERENCE.name,
    },
)
RENCONTRE = Subcategory.from_new(
    subcategories_v2.RENCONTRE,
    {
        "search_group_name": SearchGroups.CONFERENCE.name,
        "homepage_label_name": HomepageLabels.CONFERENCE.name,
    },
)
DECOUVERTE_METIERS = Subcategory.from_new(
    subcategories_v2.DECOUVERTE_METIERS,
    {
        "search_group_name": SearchGroups.CONFERENCE.name,
        "homepage_label_name": HomepageLabels.CONFERENCE.name,
    },
)
SALON = Subcategory.from_new(
    subcategories_v2.SALON,
    {
        "search_group_name": SearchGroups.CONFERENCE.name,
        "homepage_label_name": HomepageLabels.CONFERENCE.name,
    },
)
RENCONTRE_EN_LIGNE = Subcategory.from_new(
    subcategories_v2.RENCONTRE_EN_LIGNE,
    {
        "search_group_name": SearchGroups.CONFERENCE.name,
        "homepage_label_name": HomepageLabels.CONFERENCE.name,
    },
)
# endregion
# region JEU
CONCOURS = Subcategory.from_new(
    subcategories_v2.CONCOURS,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
RENCONTRE_JEU = Subcategory.from_new(
    subcategories_v2.RENCONTRE_JEU,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
ESCAPE_GAME = Subcategory.from_new(
    subcategories_v2.ESCAPE_GAME,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
EVENEMENT_JEU = Subcategory.from_new(
    subcategories_v2.EVENEMENT_JEU,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
JEU_EN_LIGNE = Subcategory.from_new(
    subcategories_v2.JEU_EN_LIGNE,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
ABO_JEU_VIDEO = Subcategory.from_new(
    subcategories_v2.ABO_JEU_VIDEO,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
ABO_LUDOTHEQUE = Subcategory.from_new(
    subcategories_v2.ABO_LUDOTHEQUE,
    {
        "search_group_name": SearchGroups.JEU.name,
        "homepage_label_name": HomepageLabels.JEU.name,
    },
)
# endregion
# region LIVRE

LIVRE_PAPIER = Subcategory.from_new(
    subcategories_v2.LIVRE_PAPIER,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
LIVRE_NUMERIQUE = Subcategory.from_new(
    subcategories_v2.LIVRE_NUMERIQUE,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
TELECHARGEMENT_LIVRE_AUDIO = Subcategory.from_new(
    subcategories_v2.TELECHARGEMENT_LIVRE_AUDIO,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
LIVRE_AUDIO_PHYSIQUE = Subcategory.from_new(
    subcategories_v2.LIVRE_AUDIO_PHYSIQUE,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
ABO_BIBLIOTHEQUE = Subcategory.from_new(
    subcategories_v2.ABO_BIBLIOTHEQUE,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
ABO_LIVRE_NUMERIQUE = Subcategory.from_new(
    subcategories_v2.ABO_LIVRE_NUMERIQUE,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
FESTIVAL_LIVRE = Subcategory.from_new(
    subcategories_v2.FESTIVAL_LIVRE,
    {
        "search_group_name": SearchGroups.LIVRE.name,
        "homepage_label_name": HomepageLabels.LIVRE.name,
    },
)
CARTE_JEUNES = Subcategory.from_new(
    subcategories_v2.CARTE_JEUNES,
    {
        "search_group_name": SearchGroups.CARTE_JEUNES.name,
        "homepage_label_name": HomepageLabels.CARTE_JEUNES.name,
    },
)
# endregion
# region VISITE

CARTE_MUSEE = Subcategory.from_new(
    subcategories_v2.CARTE_MUSEE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
ABO_MUSEE = Subcategory.from_new(
    subcategories_v2.ABO_MUSEE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
VISITE = Subcategory.from_new(
    subcategories_v2.VISITE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
VISITE_GUIDEE = Subcategory.from_new(
    subcategories_v2.VISITE_GUIDEE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
EVENEMENT_PATRIMOINE = Subcategory.from_new(
    subcategories_v2.EVENEMENT_PATRIMOINE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
VISITE_VIRTUELLE = Subcategory.from_new(
    subcategories_v2.VISITE_VIRTUELLE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
MUSEE_VENTE_DISTANCE = Subcategory.from_new(
    subcategories_v2.MUSEE_VENTE_DISTANCE,
    {
        "search_group_name": SearchGroups.VISITE.name,
        "homepage_label_name": HomepageLabels.VISITE.name,
    },
)
# endregion
# region MUSIQUE_LIVE

CONCERT = Subcategory.from_new(
    subcategories_v2.CONCERT,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
EVENEMENT_MUSIQUE = Subcategory.from_new(
    subcategories_v2.EVENEMENT_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
LIVESTREAM_MUSIQUE = Subcategory.from_new(
    subcategories_v2.LIVESTREAM_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
ABO_CONCERT = Subcategory.from_new(
    subcategories_v2.ABO_CONCERT,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
FESTIVAL_MUSIQUE = Subcategory.from_new(
    subcategories_v2.FESTIVAL_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
# endregion
# region MUSIQUE_ENREGISTREE
SUPPORT_PHYSIQUE_MUSIQUE = Subcategory.from_new(
    subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
TELECHARGEMENT_MUSIQUE = Subcategory.from_new(
    subcategories_v2.TELECHARGEMENT_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
ABO_PLATEFORME_MUSIQUE = Subcategory.from_new(
    subcategories_v2.ABO_PLATEFORME_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)
CAPTATION_MUSIQUE = Subcategory.from_new(
    subcategories_v2.CAPTATION_MUSIQUE,
    {
        "search_group_name": SearchGroups.MUSIQUE.name,
        "homepage_label_name": HomepageLabels.MUSIQUE.name,
    },
)

# endregion
# region PRATIQUE
SEANCE_ESSAI_PRATIQUE_ART = Subcategory.from_new(
    subcategories_v2.SEANCE_ESSAI_PRATIQUE_ART,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
ATELIER_PRATIQUE_ART = Subcategory.from_new(
    subcategories_v2.ATELIER_PRATIQUE_ART,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
ABO_PRATIQUE_ART = Subcategory.from_new(
    subcategories_v2.ABO_PRATIQUE_ART,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
PRATIQUE_ART_VENTE_DISTANCE = Subcategory.from_new(
    subcategories_v2.PRATIQUE_ART_VENTE_DISTANCE,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
PLATEFORME_PRATIQUE_ARTISTIQUE = Subcategory.from_new(
    subcategories_v2.PLATEFORME_PRATIQUE_ARTISTIQUE,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
LIVESTREAM_PRATIQUE_ARTISTIQUE = Subcategory.from_new(
    subcategories_v2.LIVESTREAM_PRATIQUE_ARTISTIQUE,
    {
        "search_group_name": SearchGroups.COURS.name,
        "homepage_label_name": HomepageLabels.COURS.name,
    },
)
# endregion
# region MEDIAS
ABO_PRESSE_EN_LIGNE = Subcategory.from_new(
    subcategories_v2.ABO_PRESSE_EN_LIGNE,
    {
        "search_group_name": SearchGroups.PRESSE.name,
        "homepage_label_name": HomepageLabels.PRESSE.name,
    },
)
PODCAST = Subcategory.from_new(
    subcategories_v2.PODCAST,
    {
        "search_group_name": SearchGroups.PRESSE.name,
        "homepage_label_name": HomepageLabels.PRESSE.name,
    },
)
APP_CULTURELLE = Subcategory.from_new(
    subcategories_v2.APP_CULTURELLE,
    {
        "search_group_name": SearchGroups.PRESSE.name,
        "homepage_label_name": HomepageLabels.PRESSE.name,
    },
)
# endregion
# region SPECTACLE
SPECTACLE_REPRESENTATION = Subcategory.from_new(
    subcategories_v2.SPECTACLE_REPRESENTATION,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
SPECTACLE_ENREGISTRE = Subcategory.from_new(
    subcategories_v2.SPECTACLE_ENREGISTRE,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
LIVESTREAM_EVENEMENT = Subcategory.from_new(
    subcategories_v2.LIVESTREAM_EVENEMENT,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
FESTIVAL_SPECTACLE = Subcategory.from_new(
    subcategories_v2.FESTIVAL_SPECTACLE,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
ABO_SPECTACLE = Subcategory.from_new(
    subcategories_v2.ABO_SPECTACLE,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
SPECTACLE_VENTE_DISTANCE = Subcategory.from_new(
    subcategories_v2.SPECTACLE_VENTE_DISTANCE,
    {
        "search_group_name": SearchGroups.SPECTACLE.name,
        "homepage_label_name": HomepageLabels.SPECTACLE.name,
    },
)
# endregion
# region INSTRUMENT
ACHAT_INSTRUMENT = Subcategory.from_new(
    subcategories_v2.ACHAT_INSTRUMENT,
    {
        "search_group_name": SearchGroups.INSTRUMENT.name,
        "homepage_label_name": HomepageLabels.INSTRUMENT.name,
    },
)
BON_ACHAT_INSTRUMENT = Subcategory.from_new(
    subcategories_v2.BON_ACHAT_INSTRUMENT,
    {
        "search_group_name": SearchGroups.INSTRUMENT.name,
        "homepage_label_name": HomepageLabels.INSTRUMENT.name,
    },
)
LOCATION_INSTRUMENT = Subcategory.from_new(
    subcategories_v2.LOCATION_INSTRUMENT,
    {
        "search_group_name": SearchGroups.INSTRUMENT.name,
        "homepage_label_name": HomepageLabels.INSTRUMENT.name,
    },
)
PARTITION = Subcategory.from_new(
    subcategories_v2.PARTITION,
    {
        "search_group_name": SearchGroups.INSTRUMENT.name,
        "homepage_label_name": HomepageLabels.INSTRUMENT.name,
    },
)
# endregion
# region BEAUX_ARTS
MATERIEL_ART_CREATIF = Subcategory.from_new(
    subcategories_v2.MATERIEL_ART_CREATIF,
    {
        "search_group_name": SearchGroups.MATERIEL.name,
        "homepage_label_name": HomepageLabels.MATERIEL.name,
    },
)
# endregion
# region TECHNICAL
ACTIVATION_EVENT = Subcategory.from_new(
    subcategories_v2.ACTIVATION_EVENT,
    {
        "search_group_name": SearchGroups.NONE.name,
        "homepage_label_name": HomepageLabels.NONE.name,
    },
)
ACTIVATION_THING = Subcategory.from_new(
    subcategories_v2.ACTIVATION_THING,
    {
        "search_group_name": SearchGroups.NONE.name,
        "homepage_label_name": HomepageLabels.NONE.name,
    },
)
JEU_SUPPORT_PHYSIQUE = Subcategory.from_new(
    subcategories_v2.JEU_SUPPORT_PHYSIQUE,
    {
        "search_group_name": SearchGroups.NONE.name,
        "homepage_label_name": HomepageLabels.NONE.name,
    },
)
OEUVRE_ART = Subcategory.from_new(
    subcategories_v2.OEUVRE_ART,
    {
        "search_group_name": SearchGroups.NONE.name,
        "homepage_label_name": HomepageLabels.NONE.name,
    },
)
# endregion
# endregion

ALL_SUBCATEGORIES = (
    ABO_BIBLIOTHEQUE,
    ABO_CONCERT,
    ABO_JEU_VIDEO,
    ABO_LIVRE_NUMERIQUE,
    ABO_LUDOTHEQUE,
    ABO_MEDIATHEQUE,
    ABO_MUSEE,
    ABO_PLATEFORME_MUSIQUE,
    ABO_PLATEFORME_VIDEO,
    ABO_PRATIQUE_ART,
    ABO_PRESSE_EN_LIGNE,
    ABO_SPECTACLE,
    ACHAT_INSTRUMENT,
    ACTIVATION_EVENT,
    ACTIVATION_THING,
    APP_CULTURELLE,
    ATELIER_PRATIQUE_ART,
    AUTRE_SUPPORT_NUMERIQUE,
    BON_ACHAT_INSTRUMENT,
    CAPTATION_MUSIQUE,
    CARTE_CINE_ILLIMITE,
    CARTE_CINE_MULTISEANCES,
    CARTE_JEUNES,
    CARTE_MUSEE,
    CINE_PLEIN_AIR,
    CINE_VENTE_DISTANCE,
    CONCERT,
    CONCOURS,
    CONFERENCE,
    DECOUVERTE_METIERS,
    ESCAPE_GAME,
    EVENEMENT_CINE,
    EVENEMENT_JEU,
    EVENEMENT_MUSIQUE,
    EVENEMENT_PATRIMOINE,
    FESTIVAL_CINE,
    FESTIVAL_LIVRE,
    FESTIVAL_MUSIQUE,
    FESTIVAL_SPECTACLE,
    JEU_EN_LIGNE,
    JEU_SUPPORT_PHYSIQUE,
    LIVESTREAM_EVENEMENT,
    LIVESTREAM_MUSIQUE,
    LIVESTREAM_PRATIQUE_ARTISTIQUE,
    LIVRE_AUDIO_PHYSIQUE,
    LIVRE_NUMERIQUE,
    LIVRE_PAPIER,
    LOCATION_INSTRUMENT,
    MATERIEL_ART_CREATIF,
    MUSEE_VENTE_DISTANCE,
    OEUVRE_ART,
    PARTITION,
    PLATEFORME_PRATIQUE_ARTISTIQUE,
    PRATIQUE_ART_VENTE_DISTANCE,
    PODCAST,
    RENCONTRE_EN_LIGNE,
    RENCONTRE_JEU,
    RENCONTRE,
    SALON,
    SEANCE_CINE,
    SEANCE_ESSAI_PRATIQUE_ART,
    SPECTACLE_ENREGISTRE,
    SPECTACLE_REPRESENTATION,
    SPECTACLE_VENTE_DISTANCE,
    SUPPORT_PHYSIQUE_FILM,
    SUPPORT_PHYSIQUE_MUSIQUE,
    TELECHARGEMENT_LIVRE_AUDIO,
    TELECHARGEMENT_MUSIQUE,
    VISITE_GUIDEE,
    VISITE_VIRTUELLE,
    VISITE,
    VOD,
)
ALL_SUBCATEGORIES_DICT = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES}
PERMANENT_SUBCATEGORIES = {
    subcategory.id: subcategory
    for subcategory in ALL_SUBCATEGORIES
    if not subcategory.can_expire and not subcategory.is_event
}
EXPIRABLE_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_expire}
EVENT_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.is_event}
ACTIVATION_SUBCATEGORIES = (ACTIVATION_EVENT.id, ACTIVATION_THING.id)
BOOK_WITH_ISBN = (LIVRE_PAPIER.id, LIVRE_AUDIO_PHYSIQUE.id, LIVRE_NUMERIQUE.id)

COLLECTIVE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_educational
}

WITHDRAWABLE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_withdrawable
}

assert set(subcategory.id for subcategory in ALL_SUBCATEGORIES) == set(
    subcategory.id for subcategory in locals().values() if isinstance(subcategory, Subcategory)
)

SubcategoryIdEnum = Enum("SubcategoryIdEnum", {subcategory.id: subcategory.id for subcategory in ALL_SUBCATEGORIES})  # type: ignore [misc]
SearchGroupNameEnum = Enum(  # type: ignore [misc]
    "SearchGroupNameEnum",
    {search_group_name: search_group_name for search_group_name in [c.name for c in SearchGroups]},
)
HomepageLabelNameEnum = Enum(  # type: ignore [misc]
    "(HomepageLabelNameEnum",
    {homepage_label_name: homepage_label_name for homepage_label_name in [h.name for h in HomepageLabels]},
)
OnlineOfflinePlatformChoicesEnum = Enum(  # type: ignore [misc]
    "OnlineOfflinePlatformChoicesEnum",
    {choice: choice for choice in [c.value for c in OnlineOfflinePlatformChoices]},
)
