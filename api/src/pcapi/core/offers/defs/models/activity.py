from typing import Literal

import pydantic
from pydantic import EmailStr
from pydantic import HttpUrl

from .base import Base
from .shared import extra_data as shared_extra_data
from .shared import withdrawal as shared_withdrawal


class AtelierPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ATELIER_PRATIQUE_ART"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class CinePleinAirModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CINE_PLEIN_AIR"]
    extra_data: shared_extra_data.ExtraDataCinema


class ConcoursModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONCOURS"]


class ConferenceModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONFERENCE"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class EvenementCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema


class EvenementJeuModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_JEU"]


class EvenementPatrimoineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_PATRIMOINE"]


class FestivalCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema


class FestivalLivreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_LIVRE"]


class RencontreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class RencontreJeuModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE_JEU"]


class SalonModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SALON"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class SeanceCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema


class SeanceEssaiPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_ESSAI_PRATIQUE_ART"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class VisiteLibreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE"]


class VisiteGuideeModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE_GUIDEE"]


class LivestreamMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic


class RencontreEnLigneModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["RENCONTRE_EN_LIGNE"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class LivestreamPratiqueArtistiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_PRATIQUE_ARTISTIQUE"]


class LivestreamEvenementModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_EVENEMENT"]
    extra_data: shared_extra_data.ExtraDataEvent


class AboSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ABO_SPECTACLE"]
    extra_data: shared_extra_data.ExtraDataShow


class SpectacleRepresentationModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["SPECTACLE_REPRESENTATION"]
    extra_data: shared_extra_data.ExtraDataPerformance


class FestivalSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_SPECTACLE"]
    extra_data: shared_extra_data.ExtraDataPerformance


class FestivalArtVisuelModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_ART_VISUEL"]
    extra_data: shared_extra_data.ExtraDataVisualArt


class ConcertModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["CONCERT"]
    extra_data: shared_extra_data.ExtraDataMusic


class FestivalMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic


class EvenementMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["EVENEMENT_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic
