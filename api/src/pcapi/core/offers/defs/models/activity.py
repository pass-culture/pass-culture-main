from typing import Literal

import pydantic
from pydantic import EmailStr
from pydantic import HttpUrl

from . import shared
from .base import Base
from .base import Typology


class AtelierPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ATELIER_PRATIQUE_ART"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class CinePleinAirModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CINE_PLEIN_AIR"]
    extra_data: shared.ExtraDataCinema
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class ConcoursModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONCOURS"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class ConferenceModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONFERENCE"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class EvenementCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_CINE"]
    extra_data: shared.ExtraDataCinema
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class EvenementJeuModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_JEU"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class EvenementPatrimoineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_PATRIMOINE"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class FestivalCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_CINE"]
    extra_data: shared.ExtraDataCinema
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class FestivalLivreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_LIVRE"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class RencontreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class RencontreJeuModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE_JEU"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class SalonModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SALON"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class SeanceCineModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_CINE"]
    extra_data: shared.ExtraDataCinema
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class SeanceEssaiPratiqueArtModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_ESSAI_PRATIQUE_ART"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class VisiteLibreModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class VisiteGuideeModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE_GUIDEE"]
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class LivestreamMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
    typology: Literal[Typology.ACTIVITY_ONLINE_EVENT] = Typology.ACTIVITY_ONLINE_EVENT


class RencontreEnLigneModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["RENCONTRE_EN_LIGNE"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class LivestreamPratiqueArtistiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_PRATIQUE_ARTISTIQUE"]
    typology: Literal[Typology.ACTIVITY_ONLINE_EVENT] = Typology.ACTIVITY_ONLINE_EVENT


class LivestreamEvenementModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_EVENEMENT"]
    extra_data: shared.ExtraDataEvent
    typology: Literal[Typology.ACTIVITY_ONLINE_EVENT] = Typology.ACTIVITY_ONLINE_EVENT


class AboSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ABO_SPECTACLE"]
    extra_data: shared.ExtraDataShow
    typology: Literal[Typology.ACTIVITY_RANDOM] = Typology.ACTIVITY_RANDOM


class SpectacleRepresentationModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["SPECTACLE_REPRESENTATION"]
    extra_data: shared.ExtraDataPerformance
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class FestivalSpectacleModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_SPECTACLE"]
    extra_data: shared.ExtraDataPerformance
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class FestivalArtVisuelModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_ART_VISUEL"]
    extra_data: shared.ExtraDataVisualArt
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class ConcertModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["CONCERT"]
    extra_data: shared.ExtraDataMusic
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class FestivalMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT


class EvenementMusiqueModel(Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["EVENEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
    typology: Literal[Typology.ACTIVITY_EVENT] = Typology.ACTIVITY_EVENT
