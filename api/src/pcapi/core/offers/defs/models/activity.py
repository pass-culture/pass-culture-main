from typing import Literal

import pydantic
from pydantic import EmailStr
from pydantic import HttpUrl

from . import base
from .shared import extra_data as shared_extra_data
from .shared import withdrawal as shared_withdrawal


class AtelierPratiqueArtModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ATELIER_PRATIQUE_ART"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class CinePleinAirModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CINE_PLEIN_AIR"]
    extra_data: shared_extra_data.ExtraDataCinema
    _typology: set[base.Typology] = {"activity"}


class ConcoursModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONCOURS"]
    _typology: set[base.Typology] = {"activity"}


class ConferenceModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["CONFERENCE"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class EvenementCineModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema
    _typology: set[base.Typology] = {"activity"}


class EvenementJeuModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_JEU"]
    _typology: set[base.Typology] = {"activity"}


class EvenementPatrimoineModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["EVENEMENT_PATRIMOINE"]
    _typology: set[base.Typology] = {"activity"}


class FestivalCineModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema
    _typology: set[base.Typology] = {"activity"}


class FestivalLivreModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["FESTIVAL_LIVRE"]
    _typology: set[base.Typology] = {"activity"}


class RencontreModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class RencontreJeuModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["RENCONTRE_JEU"]
    _typology: set[base.Typology] = {"activity"}


class SalonModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SALON"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class SeanceCineModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_CINE"]
    extra_data: shared_extra_data.ExtraDataCinema
    _typology: set[base.Typology] = {"activity"}


class SeanceEssaiPratiqueArtModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["SEANCE_ESSAI_PRATIQUE_ART"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class VisiteLibreModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE"]
    _typology: set[base.Typology] = {"activity"}


class VisiteGuideeModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["VISITE_GUIDEE"]
    _typology: set[base.Typology] = {"activity"}


class LivestreamMusiqueModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic
    _typology: set[base.Typology] = {"digital", "activity"}


class RencontreEnLigneModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["RENCONTRE_EN_LIGNE"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity"}


class LivestreamPratiqueArtistiqueModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_PRATIQUE_ARTISTIQUE"]
    _typology: set[base.Typology] = {"digital", "activity"}


class LivestreamEvenementModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    url: HttpUrl
    subcategory_id: Literal["LIVESTREAM_EVENEMENT"]
    extra_data: shared_extra_data.ExtraDataEvent
    _typology: set[base.Typology] = {"digital", "activity"}


class AboSpectacleModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    subcategory_id: Literal["ABO_SPECTACLE"]
    extra_data: shared_extra_data.ExtraDataShow


class SpectacleRepresentationModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["SPECTACLE_REPRESENTATION"]
    extra_data: shared_extra_data.ExtraDataPerformance
    _typology: set[base.Typology] = {"activity"}


class FestivalSpectacleModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_SPECTACLE"]
    extra_data: shared_extra_data.ExtraDataPerformance
    _typology: set[base.Typology] = {"activity"}


class FestivalArtVisuelModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_ART_VISUEL"]
    extra_data: shared_extra_data.ExtraDataVisualArt
    _typology: set[base.Typology] = {"activity"}


class ConcertModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["CONCERT"]
    extra_data: shared_extra_data.ExtraDataMusic
    _typology: set[base.Typology] = {"activity"}


class FestivalMusiqueModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["FESTIVAL_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic
    _typology: set[base.Typology] = {"activity"}


class EvenementMusiqueModel(base.Base):
    # optional for most of subcategories, but not here
    booking_email: EmailStr
    withdrawal: shared_withdrawal.WithdrawalInfo = pydantic.Field(discriminator="kind")
    subcategory_id: Literal["EVENEMENT_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic
    _typology: set[base.Typology] = {"activity"}
