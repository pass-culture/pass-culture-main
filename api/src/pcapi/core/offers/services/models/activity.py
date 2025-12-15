from typing import Annotated
from typing import Literal

import pydantic as pydantic
from pydantic import EmailStr
from pydantic import HttpUrl

from . import shared
from .base import Base


class ActivityBaseModel(Base):
    # optional for most of subcategories, but not these
    booking_email: EmailStr


class SpeakerExtraData(pydantic.BaseModel):
    speaker: Annotated[str, shared.NameString] | None = None


# NOTE(jbaudet - 12/2025): should at least the author be set? the visa?
class CinemaExtraData(pydantic.BaseModel):
    stage_director: Annotated[str, shared.NameString] | None = None
    visa: Annotated[str, shared.VisaString] | None = None
    author: Annotated[str, shared.NameString] | None = None


class AtelierPratiqueArtModel(ActivityBaseModel):
    subcategory_id: Literal["ATELIER_PRATIQUE_ART"]
    extra_data: SpeakerExtraData | None = None


class CinePleinAirModel(ActivityBaseModel):
    subcategory_id: Literal["CINE_PLEIN_AIR"]
    extra_data: CinemaExtraData | None = None


class ConcoursModel(ActivityBaseModel):
    subcategory_id: Literal["CONCOURS"]


class ConferenceModel(ActivityBaseModel):
    subcategory_id: Literal["CONFERENCE"]
    extra_data: SpeakerExtraData | None = None


class EvenementCineModel(ActivityBaseModel):
    subcategory_id: Literal["EVENEMENT_CINE"]
    extra_data: CinemaExtraData | None = None


class EvenementJeuModel(ActivityBaseModel):
    subcategory_id: Literal["EVENEMENT_JEU"]


class EvenementPatrimoineModel(ActivityBaseModel):
    subcategory_id: Literal["EVENEMENT_PATRIMOINE"]


class FestivalCineModel(ActivityBaseModel):
    subcategory_id: Literal["FESTIVAL_CINE"]
    extra_data: CinemaExtraData | None = None


class FestivalLivreModel(ActivityBaseModel):
    subcategory_id: Literal["FESTIVAL_LIVRE"]


class RencontreModel(ActivityBaseModel):
    subcategory_id: Literal["RENCONTRE"]
    extra_data: SpeakerExtraData | None = None


class RencontreJeuModel(ActivityBaseModel):
    subcategory_id: Literal["RENCONTRE_JEU"]


class SalonModel(ActivityBaseModel):
    subcategory_id: Literal["SALON"]
    extra_data: SpeakerExtraData | None = None


class SeanceCineModel(ActivityBaseModel):
    subcategory_id: Literal["SEANCE_CINE"]
    extra_data: CinemaExtraData | None = None


class SeanceEssaiPratiqueArtModel(ActivityBaseModel):
    subcategory_id: Literal["SEANCE_ESSAI_PRATIQUE_ART"]
    extra_data: SpeakerExtraData | None = None


class VisiteLibreModel(ActivityBaseModel):
    subcategory_id: Literal["VISITE"]


class VisiteGuideeModel(ActivityBaseModel):
    subcategory_id: Literal["VISITE_GUIDEE"]


class ActivityOnline(ActivityBaseModel):
    url: HttpUrl


class LivestreamMusiqueModel(ActivityOnline):
    subcategory_id: Literal["LIVESTREAM_MUSIQUE"]
    extra_data: shared.ExtraDataMusic


class RencontreEnLigneModel(ActivityOnline):
    subcategory_id: Literal["RENCONTRE_EN_LIGNE"]
    extra_data: shared.ExtraDataSpeaker


class LivestreamPratiqueArtistiqueModel(ActivityOnline):
    subcategory_id: Literal["LIVESTREAM_PRATIQUE_ARTISTIQUE"]


# NOTICE(jbaudet - 12/2025): can be an event
class LivestreamEvenementModel(ActivityBaseModel):
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_EVENEMENT"]
    extra_data: shared.ExtraDataEvent


class AboSpectacleModel(ActivityBaseModel):
    subcategory_id: Literal["ABO_SPECTACLE"]
    extra_data: shared.ExtraDataShow


class ActivityWithTicketBaseModel(ActivityBaseModel):
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")


class SpectacleRepresentationModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["SPECTACLE_REPRESENTATION"]
    extra_data: shared.ExtraDataPerformance


class FestivalSpectacleModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["FESTIVAL_SPECTACLE"]
    extra_data: shared.ExtraDataPerformance


class FestivalArtVisuelModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["FESTIVAL_ART_VISUEL"]
    extra_data: shared.ExtraDataVisualArt


class ConcertModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["CONCERT"]
    extra_data: shared.ExtraDataMusic


class FestivalMusiqueModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["FESTIVAL_MUSIQUE"]
    extra_data: shared.ExtraDataMusic


class EvenementMusiqueModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal["EVENEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
