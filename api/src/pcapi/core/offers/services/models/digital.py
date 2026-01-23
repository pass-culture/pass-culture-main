from typing import Literal

from pydantic import HttpUrl

from . import shared
from .base import Base


class TelechargementMusiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusicWithEan


class LivreNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["LIVRE_NUMERIQUE"]
    extra_data: shared.ExtraDataBook


class PlateformePratiqueArtistiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PLATEFORME_PRATIQUE_ARTISTIQUE"]


class AutreSupportNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["AUTRE_SUPPORT_NUMERIQUE"]


class MuseeVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["MUSEE_VENTE_DISTANCE"]


class VisiteVirtuelleModel(Base):
    url: HttpUrl
    subcategory_id: Literal["VISITE_VIRTUELLE"]


class PratiqueArtVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PRATIQUE_ART_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataSpeaker


class AboPlateformeVideoModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_VIDEO"]


class AboPresseEnLigneModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PRESSE_EN_LIGNE"]


class AppCulturelleModel(Base):
    url: HttpUrl
    subcategory_id: Literal["APP_CULTURELLE"]


class JeuEnLigneModel(Base):
    url: HttpUrl
    subcategory_id: Literal["JEU_EN_LIGNE"]
    extra_data: shared.ExtraDataEan


class CineVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["CINE_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataCine


class AboLivreNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_LIVRE_NUMERIQUE"]


class AboJeuVideoModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_JEU_VIDEO"]


class PodcastModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PODCAST"]


class TelechargementLivreAudioModel(Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_LIVRE_AUDIO"]
    extra_data: shared.ExtraDataAuthor


class AboPlateformeMusiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_MUSIQUE"]


class VODModel(Base):
    url: HttpUrl
    subcategory_id: Literal["VOD"]


class DigitalShowModel(Base):
    url: HttpUrl
    extra_data: shared.ExtraDataDigitalShow


class SpectacleEnregistreModel(DigitalShowModel):
    subcategory_id: Literal["SPECTACLE_ENREGISTRE"]


class SpectacleVenteDistanceModel(DigitalShowModel):
    subcategory_id: Literal["SPECTACLE_VENTE_DISTANCE"]
