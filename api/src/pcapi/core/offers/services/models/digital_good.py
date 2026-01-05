from typing import Literal

from pcapi.core.categories import subcategories

from .digital import DigitalBaseModel
from . import shared


class TelechargementMusiqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.TELECHARGEMENT_MUSIQUE.id]
    extra_data: shared.ExtraDataMusicWithEan


class LivreNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.LIVRE_NUMERIQUE.id]
    extra_data: shared.ExtraDataBook


class PlateformePratiqueArtistiqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id]


class AutreSupportNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.AUTRE_SUPPORT_NUMERIQUE.id]


class MuseeVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.MUSEE_VENTE_DISTANCE.id]


class VisiteVirtuelleModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.VISITE_VIRTUELLE.id]


class PratiqueArtVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.PRATIQUE_ART_VENTE_DISTANCE.id]
    extra_data: shared.ExtraDataSpeaker


class AboPlateformeVideoModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.ABO_PLATEFORME_VIDEO.id]


class AboPresseEnLigneModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.ABO_PRESSE_EN_LIGNE.id]


class AppCulturelleModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.APP_CULTURELLE.id]


class JeuEnLigneModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.JEU_EN_LIGNE.id]
    extra_data: shared.ExtraDataEan


class CineVenteDistanceModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.CINE_VENTE_DISTANCE.id]
    extra_data: shared.ExtraDataCine


class AboLivreNumeriqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.ABO_LIVRE_NUMERIQUE.id]


class AboJeuVideoModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.ABO_JEU_VIDEO.id]


class PodcastModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.PODCAST.id]


class TelechargementLivreAudioModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.TELECHARGEMENT_LIVRE_AUDIO.id]
    extra_data: shared.ExtraDataAuthor


class AboPlateformeMusiqueModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.ABO_PLATEFORME_MUSIQUE.id]


class VODModel(DigitalBaseModel):
    subcategory_id: Literal[subcategories.VOD.id]
