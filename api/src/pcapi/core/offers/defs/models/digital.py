from typing import Literal

from pydantic import HttpUrl

from . import shared
from .base import Base
from .base import Typology


class TelechargementMusiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusicWithEan
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class LivreNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["LIVRE_NUMERIQUE"]
    extra_data: shared.ExtraDataBook
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class PlateformePratiqueArtistiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PLATEFORME_PRATIQUE_ARTISTIQUE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class AutreSupportNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["AUTRE_SUPPORT_NUMERIQUE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class MuseeVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["MUSEE_VENTE_DISTANCE"]
    typology: Literal[Typology.UNSPECIFIED] = Typology.UNSPECIFIED


class VisiteVirtuelleModel(Base):
    url: HttpUrl
    subcategory_id: Literal["VISITE_VIRTUELLE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class PratiqueArtVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PRATIQUE_ART_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.UNSPECIFIED] = Typology.UNSPECIFIED


class AboPlateformeVideoModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_VIDEO"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class AboPresseEnLigneModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PRESSE_EN_LIGNE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class AppCulturelleModel(Base):
    url: HttpUrl
    subcategory_id: Literal["APP_CULTURELLE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class JeuEnLigneModel(Base):
    url: HttpUrl
    subcategory_id: Literal["JEU_EN_LIGNE"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class CineVenteDistanceModel(Base):
    url: HttpUrl
    subcategory_id: Literal["CINE_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataCinema
    typology: Literal[Typology.UNSPECIFIED] = Typology.UNSPECIFIED


class AboLivreNumeriqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_LIVRE_NUMERIQUE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class AboJeuVideoModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_JEU_VIDEO"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class PodcastModel(Base):
    url: HttpUrl
    subcategory_id: Literal["PODCAST"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class TelechargementLivreAudioModel(Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_LIVRE_AUDIO"]
    extra_data: shared.ExtraDataAuthor
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class AboPlateformeMusiqueModel(Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_MUSIQUE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class VODModel(Base):
    url: HttpUrl
    subcategory_id: Literal["VOD"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class SpectacleEnregistreModel(Base):
    url: HttpUrl
    extra_data: shared.ExtraDataDigitalShow
    subcategory_id: Literal["SPECTACLE_ENREGISTRE"]
    typology: Literal[Typology.DIGITAL] = Typology.DIGITAL


class SpectacleVenteDistanceModel(Base):
    url: HttpUrl
    extra_data: shared.ExtraDataDigitalShow
    subcategory_id: Literal["SPECTACLE_VENTE_DISTANCE"]
    typology: Literal[Typology.UNSPECIFIED] = Typology.UNSPECIFIED
