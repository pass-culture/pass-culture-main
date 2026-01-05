from enum import Enum
from typing import Annotated

import pydantic as pydantic_v2
from pydantic import AfterValidator
from pydantic import BeforeValidator
from pydantic import StringConstraints

from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.providers import constants


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
THINGS_WITH_EAN = {
    subcategories.LIVRE_PAPIER.id: subcategories.LIVRE_PAPIER,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
THINGS_RANDOM = {
    subcategories.ABO_BIBLIOTHEQUE.id: subcategories.ABO_BIBLIOTHEQUE,
    subcategories.ABO_CONCERT.id: subcategories.ABO_CONCERT,
    subcategories.ABO_MEDIATHEQUE.id: subcategories.ABO_MEDIATHEQUE,
    subcategories.ABO_PRATIQUE_ART.id: subcategories.ABO_PRATIQUE_ART,
    subcategories.ACHAT_INSTRUMENT.id: subcategories.ACHAT_INSTRUMENT,
    subcategories.CARTE_CINE_ILLIMITE.id: subcategories.CARTE_CINE_ILLIMITE,
    subcategories.CARTE_CINE_MULTISEANCES.id: subcategories.CARTE_CINE_MULTISEANCES,
    subcategories.CARTE_JEUNES.id: subcategories.CARTE_JEUNES,
    subcategories.CARTE_MUSEE.id: subcategories.CARTE_MUSEE,
    subcategories.ESCAPE_GAME.id: subcategories.ESCAPE_GAME,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id: subcategories.LIVRE_AUDIO_PHYSIQUE,
    subcategories.LOCATION_INSTRUMENT.id: subcategories.LOCATION_INSTRUMENT,
    subcategories.MATERIEL_ART_CREATIF.id: subcategories.MATERIEL_ART_CREATIF,
    subcategories.PARTITION.id: subcategories.PARTITION,
    subcategories.SUPPORT_PHYSIQUE_FILM.id: subcategories.SUPPORT_PHYSIQUE_FILM,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
DIGITAL_THING = {
    subcategories.TELECHARGEMENT_MUSIQUE.id: subcategories.TELECHARGEMENT_MUSIQUE,
    subcategories.LIVRE_NUMERIQUE.id: subcategories.LIVRE_NUMERIQUE,
    subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id: subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE,
    subcategories.AUTRE_SUPPORT_NUMERIQUE.id: subcategories.AUTRE_SUPPORT_NUMERIQUE,
    subcategories.MUSEE_VENTE_DISTANCE.id: subcategories.MUSEE_VENTE_DISTANCE,
    subcategories.VISITE_VIRTUELLE.id: subcategories.VISITE_VIRTUELLE,
    subcategories.PRATIQUE_ART_VENTE_DISTANCE.id: subcategories.PRATIQUE_ART_VENTE_DISTANCE,
    subcategories.ABO_PLATEFORME_VIDEO.id: subcategories.ABO_PLATEFORME_VIDEO,
    subcategories.ABO_PRESSE_EN_LIGNE.id: subcategories.ABO_PRESSE_EN_LIGNE,
    subcategories.APP_CULTURELLE.id: subcategories.APP_CULTURELLE,
    subcategories.JEU_EN_LIGNE.id: subcategories.JEU_EN_LIGNE,
    subcategories.CINE_VENTE_DISTANCE.id: subcategories.CINE_VENTE_DISTANCE,
    subcategories.ABO_LIVRE_NUMERIQUE.id: subcategories.ABO_LIVRE_NUMERIQUE,
    subcategories.ABO_JEU_VIDEO.id: subcategories.ABO_JEU_VIDEO,
    subcategories.PODCAST.id: subcategories.PODCAST,
    subcategories.TELECHARGEMENT_LIVRE_AUDIO.id: subcategories.TELECHARGEMENT_LIVRE_AUDIO,
    subcategories.ABO_PLATEFORME_MUSIQUE.id: subcategories.ABO_PLATEFORME_MUSIQUE,
    subcategories.VOD.id: subcategories.VOD,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
DIGITAL_ACTIVITY = {
    subcategories.SPECTACLE_ENREGISTRE.id: subcategories.SPECTACLE_ENREGISTRE,
    subcategories.SPECTACLE_VENTE_DISTANCE.id: subcategories.SPECTACLE_VENTE_DISTANCE,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
CANNOT_BE_CREATED = {
    subcategories.ACTIVATION_EVENT.id: subcategories.ACTIVATION_EVENT,
    subcategories.CAPTATION_MUSIQUE.id: subcategories.CAPTATION_MUSIQUE,
    subcategories.OEUVRE_ART.id: subcategories.OEUVRE_ART,
    subcategories.BON_ACHAT_INSTRUMENT.id: subcategories.BON_ACHAT_INSTRUMENT,
    subcategories.ACTIVATION_THING.id: subcategories.ACTIVATION_THING,
    subcategories.ABO_LUDOTHEQUE.id: subcategories.ABO_LUDOTHEQUE,
    subcategories.JEU_SUPPORT_PHYSIQUE.id: subcategories.JEU_SUPPORT_PHYSIQUE,
    subcategories.DECOUVERTE_METIERS.id: subcategories.DECOUVERTE_METIERS,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_SUBSCRIPTION = {
    subcategories.ABO_SPECTACLE.id: subcategories.ABO_SPECTACLE,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_ONLINE = {
    subcategories.LIVESTREAM_MUSIQUE.id: subcategories.LIVESTREAM_MUSIQUE,
    subcategories.RENCONTRE_EN_LIGNE.id: subcategories.RENCONTRE_EN_LIGNE,
    subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id: subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_ONLINE_EVENT = {
    subcategories.LIVESTREAM_EVENEMENT.id: subcategories.LIVESTREAM_EVENEMENT,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_WITHDRAWABLE = {
    subcategories.SPECTACLE_REPRESENTATION.id: subcategories.SPECTACLE_REPRESENTATION,
    subcategories.FESTIVAL_SPECTACLE.id: subcategories.FESTIVAL_SPECTACLE,
    subcategories.FESTIVAL_ART_VISUEL.id: subcategories.FESTIVAL_ART_VISUEL,
    subcategories.CONCERT.id: subcategories.CONCERT,
    subcategories.FESTIVAL_MUSIQUE.id: subcategories.FESTIVAL_MUSIQUE,
    subcategories.EVENEMENT_MUSIQUE.id: subcategories.EVENEMENT_MUSIQUE,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_COULD_BE_AN_EVENT = {
    subcategories.ATELIER_PRATIQUE_ART.id: subcategories.ATELIER_PRATIQUE_ART,
    subcategories.CINE_PLEIN_AIR.id: subcategories.CINE_PLEIN_AIR,
    subcategories.CONCOURS.id: subcategories.CONCOURS,
    subcategories.CONFERENCE.id: subcategories.CONFERENCE,
    subcategories.EVENEMENT_CINE.id: subcategories.EVENEMENT_CINE,
    subcategories.EVENEMENT_JEU.id: subcategories.EVENEMENT_JEU,
    subcategories.EVENEMENT_PATRIMOINE.id: subcategories.EVENEMENT_PATRIMOINE,
    subcategories.FESTIVAL_CINE.id: subcategories.FESTIVAL_CINE,
    subcategories.FESTIVAL_LIVRE.id: subcategories.FESTIVAL_LIVRE,
    subcategories.RENCONTRE.id: subcategories.RENCONTRE,
    subcategories.RENCONTRE_JEU.id: subcategories.RENCONTRE_JEU,
    subcategories.SALON.id: subcategories.SALON,
    subcategories.SEANCE_CINE.id: subcategories.SEANCE_CINE,
    subcategories.SEANCE_ESSAI_PRATIQUE_ART.id: subcategories.SEANCE_ESSAI_PRATIQUE_ART,
    subcategories.VISITE_LIBRE.id: subcategories.VISITE_LIBRE,
    subcategories.VISITE_GUIDEE.id: subcategories.VISITE_GUIDEE,
}


# needed because original VenueTypeCode uses pydantic v1... which
# is not compatible with v2 model used here.
VenueTypeCode = Enum("VenueTypeCode", dict(offerers_schemas.VenueTypeCode.__members__))


def parse_venue_type_code(code: str | VenueTypeCode) -> VenueTypeCode:
    if isinstance(code, VenueTypeCode):
        return code
    return VenueTypeCode[code]


class Venue(pydantic_v2.BaseModel):
    id: int
    code: Annotated[VenueTypeCode, BeforeValidator(parse_venue_type_code)]
    has_ticketing: bool = False


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1024)]
GtlIdString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]

# could probably be a little bit more strict, but let's be safe for now
VisaString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=64)]

EanString = Annotated[str, AfterValidator(lambda s: len(s) in (8, 13, 128))]

MusicType = Annotated[int, AfterValidator(lambda t: t in music.MUSIC_SLUG_BY_GTL_ID)]
MusicSubType = Annotated[int, AfterValidator(lambda t: t in music.MUSIC_SUB_TYPES_BY_SLUG)]

ShowType = Annotated[int, AfterValidator(lambda t: t in music.SHOW_TYPES_LABEL_BY_CODE)]
ShowSubType = Annotated[int, AfterValidator(lambda t: t in music.SHOW_SUB_TYPES_BY_CODE)]

TiteLiveMusicGenres = Annotated[str, AfterValidator(lambda g: g in constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID)]


# TODO(jbaudet - 12/2025): warning: fields should be transformed
# -> same as above
class ShowTypeModel(pydantic_v2.BaseModel):
    show_type: ShowType
    show_sub_type: ShowSubType


class ExtraData(pydantic_v2.BaseModel):
    model_config = pydantic_v2.ConfigDict(extra="forbid")


class ExtraDataEan(ExtraData):
    ean: EanString | None = None


class ExtraDataShow(ExtraData):
    show_sub_type: ShowSubType
    show_type: ShowType
    author: NameString | None = None
    performer: NameString | None = None
    stage_director: NameString | None = None


class ConcertExtraData(ExtraData):
    music_type: MusicType | None
    gtl_id: TiteLiveMusicGenres | None = None


class ExtraDataMusic(ExtraData):
    performer: NameString | None = None
    author: NameString | None = None
    music_type: MusicType | None = None
    music_sub_type: MusicSubType | None = None
    gtl_id: TiteLiveMusicGenres | None = None


class ExtraDataMusicWithEan(ExtraDataMusic, ExtraDataEan):
    pass


class ExtraDataCine(ExtraData):
    visa: VisaString | None = None
    stage_director: NameString | None = None
    author: NameString | None = None


class ExtraDataSpeaker(ExtraData):
    speaker: NameString | None = None


class ExtraDataEvent(ExtraData):
    show_type: ShowType
    show_sub_type: ShowSubType
    stage_director: NameString | None = None
    performer: NameString | None = None
    author: NameString | None = None


class ExtraDataArtistic(ExtraData):
    show_type: ShowType
    show_sub_type: ShowSubType
    music_type: MusicType
    music_sub_type: MusicSubType
    gtl_id: TiteLiveMusicGenres


class ExtraDataAuthor(ExtraData):
    author: NameString | None = None


class ExtraDataBook(ExtraDataEan, ExtraDataAuthor):
    pass


class ExtraDataBookWithGtl(ExtraDataBook):
    gtl_id: GtlIdString | None = None


class ExtraDataCine(ExtraData):
    visa: VisaString | None = None
    stage_director: NameString | None = None
    author: NameString | None = None


class ExtraDataSpeaker(ExtraData):
    speaker: NameString | None = None


class ExtraDataEvent(ExtraData):
    show_type: ShowType
    show_sub_type: ShowSubType
    stage_director: NameString | None = None
    performer: NameString | None = None
    author: NameString | None = None


class ExtraDataArtistic(ExtraData):
    show_type: ShowType
    show_sub_type: ShowSubType
    music_type: MusicType
    music_sub_type: MusicSubType
    gtl_id: TiteLiveMusicGenres
