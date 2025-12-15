from typing import Literal

from pydantic import HttpUrl

from . import shared
from .base import Base


class DigitalBaseModel(Base):
    url: HttpUrl


class TelechargementMusiqueModel(DigitalBaseModel):
    subcategory_id: Literal["TELECHARGEMENT_MUSIQUE"]
    extra_data: shared.ExtraDataMusicWithEan


class LivreNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal["LIVRE_NUMERIQUE"]
    extra_data: shared.ExtraDataBook


class PlateformePratiqueArtistiqueModel(DigitalBaseModel):
    subcategory_id: Literal["PLATEFORME_PRATIQUE_ARTISTIQUE"]


class AutreSupportNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal["AUTRE_SUPPORT_NUMERIQUE"]


class MuseeVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal["MUSEE_VENTE_DISTANCE"]


class VisiteVirtuelleModel(DigitalBaseModel):
    subcategory_id: Literal["VISITE_VIRTUELLE"]


class PratiqueArtVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal["PRATIQUE_ART_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataSpeaker


class AboPlateformeVideoModel(DigitalBaseModel):
    subcategory_id: Literal["ABO_PLATEFORME_VIDEO"]


class AboPresseEnLigneModel(DigitalBaseModel):
    subcategory_id: Literal["ABO_PRESSE_EN_LIGNE"]


class AppCulturelleModel(DigitalBaseModel):
    subcategory_id: Literal["APP_CULTURELLE"]


class JeuEnLigneModel(DigitalBaseModel):
    subcategory_id: Literal["JEU_EN_LIGNE"]
    extra_data: shared.ExtraDataEan


class CineVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal["CINE_VENTE_DISTANCE"]
    extra_data: shared.ExtraDataCine


class AboLivreNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal["ABO_LIVRE_NUMERIQUE"]


class AboJeuVideoModel(DigitalBaseModel):
    subcategory_id: Literal["ABO_JEU_VIDEO"]


class PodcastModel(DigitalBaseModel):
    subcategory_id: Literal["PODCAST"]


class TelechargementLivreAudioModel(DigitalBaseModel):
    subcategory_id: Literal["TELECHARGEMENT_LIVRE_AUDIO"]
    extra_data: shared.ExtraDataAuthor


class AboPlateformeMusiqueModel(DigitalBaseModel):
    subcategory_id: Literal["ABO_PLATEFORME_MUSIQUE"]


class VODModel(DigitalBaseModel):
    subcategory_id: Literal["VOD"]


class DigitalShowModel(DigitalBaseModel):
    extra_data: shared.ExtraDataDigitalShow


class SpectacleEnregistreModel(DigitalShowModel):
    subcategory_id: Literal["SPECTACLE_ENREGISTRE"]


class SpectacleVenteDistanceModel(DigitalShowModel):
    subcategory_id: Literal["SPECTACLE_VENTE_DISTANCE"]
