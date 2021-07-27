from typing import Optional

from pcapi.models import ThingType
from pcapi.models.offer_type import ALL_OFFER_TYPES_DICT

from . import subcategories


CAN_CREATE_FROM_ISBN_SUBCATEGORIES = (
    subcategories.LIVRE_PAPIER.id,
    subcategories.LIVRE_NUMERIQUE.id,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id,
)


def can_create_from_isbn(subcategory_id: Optional[str], offer_type: Optional[str]) -> bool:
    # FIXME(rchaffal, 2021-07-08): remove once all offers and product have subcategoryId
    if subcategory_id:
        return subcategory_id in CAN_CREATE_FROM_ISBN_SUBCATEGORIES
    return offer_type == str(ThingType.LIVRE_EDITION)


def get_subcategory_from_type(offer_type: str, is_virtual_venue: bool):
    if not ALL_OFFER_TYPES_DICT[offer_type]["offlineOnly"] and not ALL_OFFER_TYPES_DICT[offer_type]["onlineOnly"]:
        if is_virtual_venue:
            return ONLINE_MAPPING_SUBCATEGORY_FROM_TYPE[offer_type]
        return OFFLINE_MAPPING_SUBCATEGORY_FROM_TYPE[offer_type]
    return REGULAR_MAPPING_SUBCATEGORY_FROM_TYPE[offer_type]


REGULAR_MAPPING_SUBCATEGORY_FROM_TYPE = {
    "EventType.ACTIVATION": subcategories.ACTIVATION_EVENT.id,
    "EventType.CINEMA": subcategories.SEANCE_CINE.id,
    "EventType.CONFERENCE_DEBAT_DEDICACE": subcategories.CONFERENCE.id,
    "EventType.JEUX": subcategories.EVENEMENT_JEU.id,
    "EventType.MUSEES_PATRIMOINE": subcategories.VISITE.id,
    "EventType.MUSIQUE": subcategories.CONCERT.id,
    "EventType.PRATIQUE_ARTISTIQUE": subcategories.ATELIER_PRATIQUE_ART.id,
    "EventType.SPECTACLE_VIVANT": subcategories.SPECTACLE_REPRESENTATION.id,
    "ThingType.ACTIVATION": subcategories.ACTIVATION_THING.id,
    "ThingType.CINEMA_ABO": subcategories.CARTE_CINE_MULTISEANCES.id,
    "ThingType.CINEMA_CARD": subcategories.CINE_VENTE_DISTANCE.id,
    "ThingType.INSTRUMENT": subcategories.ACHAT_INSTRUMENT.id,
    "ThingType.JEUX": subcategories.JEU_SUPPORT_PHYSIQUE.id,
    "ThingType.JEUX_VIDEO": subcategories.JEU_EN_LIGNE.id,
    "ThingType.JEUX_VIDEO_ABO": subcategories.ABO_JEU_VIDEO.id,
    "ThingType.LIVRE_AUDIO": subcategories.LIVRE_NUMERIQUE.id,
    "ThingType.MATERIEL_ART_CREA": subcategories.MATERIEL_ART_CREATIF.id,
    "ThingType.MUSIQUE_ABO": subcategories.ABO_CONCERT.id,
    "ThingType.OEUVRE_ART": subcategories.OEUVRE_ART.id,
    "ThingType.PRATIQUE_ARTISTIQUE_ABO": subcategories.ABO_PRATIQUE_ART.id,
    "ThingType.PRESSE_ABO": subcategories.ABO_PRESSE_EN_LIGNE.id,
    "ThingType.SPECTACLE_VIVANT_ABO": subcategories.ABO_SPECTACLE.id,
}
OFFLINE_MAPPING_SUBCATEGORY_FROM_TYPE = {
    "ThingType.MUSEES_PATRIMOINE_ABO": subcategories.CARTE_MUSEE.id,
    "ThingType.MUSIQUE": subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
    "ThingType.AUDIOVISUEL": subcategories.SUPPORT_PHYSIQUE_FILM.id,
    "ThingType.LIVRE_EDITION": subcategories.LIVRE_PAPIER.id,
}
ONLINE_MAPPING_SUBCATEGORY_FROM_TYPE = {
    "ThingType.MUSEES_PATRIMOINE_ABO": subcategories.MUSEE_VENTE_DISTANCE.id,
    "ThingType.MUSIQUE": subcategories.TELECHARGEMENT_MUSIQUE.id,
    "ThingType.AUDIOVISUEL": subcategories.VOD.id,
    "ThingType.LIVRE_EDITION": subcategories.LIVRE_NUMERIQUE.id,
}
