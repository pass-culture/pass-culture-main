from typing import Literal

from pcapi.core.categories import subcategories

from .digital import DigitalBaseModel


class TelechargementMusiqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.TELECHARGEMENT_MUSIQUE.id]


class LivreNumeriqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.LIVRE_NUMERIQUE.id]


class PlateformePratiqueArtistiqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id]


class AutreSupportNumeriqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.AUTRE_SUPPORT_NUMERIQUE.id]


class MuseeVenteDistanceModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.MUSEE_VENTE_DISTANCE.id]


class VisiteVirtuelleModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.VISITE_VIRTUELLE.id]


class PratiqueArtVenteDistanceModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.PRATIQUE_ART_VENTE_DISTANCE.id]


class AboPlateformeVideoModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.ABO_PLATEFORME_VIDEO.id]


class AboPresseEnLigneModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.ABO_PRESSE_EN_LIGNE.id]


class AppCulturelleModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.APP_CULTURELLE.id]


class JeuEnLigneModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.JEU_EN_LIGNE.id]


class CineVenteDistanceModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.CINE_VENTE_DISTANCE.id]


class AboLivreNumeriqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.ABO_LIVRE_NUMERIQUE.id]


class AboJeuVideoModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.ABO_JEU_VIDEO.id]


class PodcastModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.PODCAST.id]


class TelechargementLivreAudioModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.TELECHARGEMENT_LIVRE_AUDIO.id]


class AboPlateformeMusiqueModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.ABO_PLATEFORME_MUSIQUE.id]


class VODModel(DigitalBaseModel):
    subcategoryId: Literal[subcategories.VOD.id]
