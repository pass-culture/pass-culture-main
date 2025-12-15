from typing import Literal

import pydantic
from pydantic import EmailStr
from pydantic import HttpUrl

from . import shared
from .base import Base


class AtelierPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ATELIER_PRATIQUE_ART"]
    extra_data: shared.ExtraDataSpeaker


class CinePleinAirModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CINE_PLEIN_AIR"]
    extra_data: shared.ExtraDataCinema


class ConcoursModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONCOURS"]


class ConferenceModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONFERENCE"]
    extra_data: shared.ExtraDataSpeaker


class EvenementCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_CINE"]
    extra_data: shared.ExtraDataCinema


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
    extra_data: shared.ExtraDataCinema


class FestivalLivreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_LIVRE"]


class RencontreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE"]
    extra_data: shared.ExtraDataSpeaker


class RencontreJeuModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE_JEU"]


class SalonModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SALON"]
    extra_data: shared.ExtraDataSpeaker


class SeanceCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_CINE"]
    extra_data: shared.ExtraDataCinema


class SeanceEssaiPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_ESSAI_PRATIQUE_ART"]
    extra_data: shared.ExtraDataSpeaker


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
    extra_data: shared.ExtraDataMusic


class RencontreEnLigneModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["RENCONTRE_EN_LIGNE"]
    extra_data: shared.ExtraDataSpeaker


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
    extra_data: shared.ExtraDataEvent


class AboSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ABO_SPECTACLE"]
    extra_data: shared.ExtraDataShow


class SpectacleRepresentationModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["SPECTACLE_REPRESENTATION"]
    extra_data: shared.ExtraDataPerformance


class FestivalSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_SPECTACLE"]
    extra_data: shared.ExtraDataPerformance


class FestivalArtVisuelModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_ART_VISUEL"]
    extra_data: shared.ExtraDataVisualArt


class ConcertModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["CONCERT"]
    extra_data: shared.ExtraDataMusic


class FestivalMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_MUSIQUE"]
    extra_data: shared.ExtraDataMusic


class EvenementMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["EVENEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
