from typing import Literal

from pydantic import HttpUrl

from . import base
from .shared import extra_data as shared_extra_data


class TelechargementMusiqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusicWithEan
    _typology: set[base.Typology] = {"digital"}


class LivreNumeriqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["LIVRE_NUMERIQUE"]
    extra_data: shared_extra_data.ExtraDataBook
    _typology: set[base.Typology] = {"digital"}


class PlateformePratiqueArtistiqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["PLATEFORME_PRATIQUE_ARTISTIQUE"]
    _typology: set[base.Typology] = {"digital"}


class AutreSupportNumeriqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["AUTRE_SUPPORT_NUMERIQUE"]
    _typology: set[base.Typology] = {"digital"}


class MuseeVenteDistanceModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["MUSEE_VENTE_DISTANCE"]


class VisiteVirtuelleModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["VISITE_VIRTUELLE"]
    _typology: set[base.Typology] = {"digital"}


class PratiqueArtVenteDistanceModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["PRATIQUE_ART_VENTE_DISTANCE"]
    extra_data: shared_extra_data.ExtraDataSpeaker


class AboPlateformeVideoModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_VIDEO"]
    _typology: set[base.Typology] = {"digital"}


class AboPresseEnLigneModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PRESSE_EN_LIGNE"]
    _typology: set[base.Typology] = {"digital"}


class AppCulturelleModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["APP_CULTURELLE"]
    _typology: set[base.Typology] = {"digital"}


class JeuEnLigneModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["JEU_EN_LIGNE"]
    extra_data: shared_extra_data.ExtraDataEan
    _typology: set[base.Typology] = {"digital"}


class CineVenteDistanceModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["CINE_VENTE_DISTANCE"]
    extra_data: shared_extra_data.ExtraDataCinema


class AboLivreNumeriqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_LIVRE_NUMERIQUE"]
    _typology: set[base.Typology] = {"digital"}


class AboJeuVideoModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_JEU_VIDEO"]
    _typology: set[base.Typology] = {"digital"}


class PodcastModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["PODCAST"]
    _typology: set[base.Typology] = {"digital"}


class TelechargementLivreAudioModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["TELECHARGEMENT_LIVRE_AUDIO"]
    extra_data: shared_extra_data.ExtraDataAuthor
    _typology: set[base.Typology] = {"digital"}


class AboPlateformeMusiqueModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["ABO_PLATEFORME_MUSIQUE"]
    _typology: set[base.Typology] = {"digital"}


class VODModel(base.Base):
    url: HttpUrl
    subcategory_id: Literal["VOD"]
    _typology: set[base.Typology] = {"digital"}


class SpectacleEnregistreModel(base.Base):
    url: HttpUrl
    extra_data: shared_extra_data.ExtraDataEvent
    subcategory_id: Literal["SPECTACLE_ENREGISTRE"]
    _typology: set[base.Typology] = {"digital"}


class SpectacleVenteDistanceModel(base.Base):
    url: HttpUrl
    extra_data: shared_extra_data.ExtraDataEvent
    subcategory_id: Literal["SPECTACLE_VENTE_DISTANCE"]
