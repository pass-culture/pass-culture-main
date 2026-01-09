from typing import Annotated
from typing import Literal

import pydantic as pydantic_v2

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


class SpeakerExtraData(pydantic_v2.BaseModel):
    speaker: Annotated[str, shared.NameString] | None = None


# NOTE(jbaudet - 12/2025): should at least the author be set? the visa?
class CinemaExtraData(pydantic_v2.BaseModel):
    stage_director: Annotated[str, shared.NameString] | None = None
    visa: Annotated[str, shared.VisaString] | None = None
    author: Annotated[str, shared.NameString] | None = None


class AtelierPratiqueArtModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.ATELIER_PRATIQUE_ART.id]
    extra_data: SpeakerExtraData | None = None


class CinePleinAirModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.CINE_PLEIN_AIR.id]
    extra_data: CinemaExtraData | None = None


class ConcoursModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.CONCOURS.id]


class ConferenceModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.CONFERENCE.id]
    extra_data: SpeakerExtraData | None = None


class EvenementCineModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.EVENEMENT_CINE.id]
    extra_data: CinemaExtraData | None = None


class EvenementJeuModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.EVENEMENT_JEU.id]


class EvenementPatrimoineModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.EVENEMENT_PATRIMOINE.id]


class FestivalCineModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.FESTIVAL_CINE.id]
    extra_data: CinemaExtraData | None = None


class FestivalLivreModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.FESTIVAL_LIVRE.id]


class RencontreModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.RENCONTRE.id]
    extra_data: SpeakerExtraData | None = None


class RencontreJeuModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.RENCONTRE_JEU.id]


class SalonModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.SALON.id]
    extra_data: SpeakerExtraData | None = None


class SeanceCineModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.SEANCE_CINE.id]
    extra_data: CinemaExtraData | None = None


class SeanceEssaiPratiqueArtModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.SEANCE_ESSAI_PRATIQUE_ART.id]
    extra_data: SpeakerExtraData | None = None


class VisiteLibreModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.VISITE_LIBRE.id]


class VisiteGuideeModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.VISITE_GUIDEE.id]
