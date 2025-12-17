from typing import Literal

from pcapi.core.categories import subcategories

from .things import ThingsBaseModel


class AboBibliothequeModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ABO_BIBLIOTHEQUE.id]


class AboConcertModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ABO_CONCERT.id]


class AboMediathequeModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ABO_MEDIATHEQUE.id]


class AboPratiqueArtModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ABO_PRATIQUE_ART.id]


class AchatInstrumentModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ACHAT_INSTRUMENT.id]


class CarteCineIllimiteModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.CARTE_CINE_ILLIMITE.id]


class CarteCineUultiseancesModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.CARTE_CINE_MULTISEANCES.id]


class CarteJeunesModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.CARTE_JEUNES.id]


class CarteMuseeModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.CARTE_MUSEE.id]


class EscapeGameModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.ESCAPE_GAME.id]


class LivreAudioPhysiqueModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.LIVRE_AUDIO_PHYSIQUE.id]


class LocationInstrumentModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.LOCATION_INSTRUMENT.id]


class MaterielArtCreatifModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.MATERIEL_ART_CREATIF.id]


class PartitionModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.PARTITION.id]


class SupportPhysiqueFilmModel(ThingsBaseModel):
    subcategoryId: Literal[subcategories.SUPPORT_PHYSIQUE_FILM.id]
