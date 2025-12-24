from typing import Literal

from pcapi.core.categories import subcategories

from .things import ThingsBaseModel


class AboBibliothequeModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ABO_BIBLIOTHEQUE.id]


class AboConcertModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ABO_CONCERT.id]


class AboMediathequeModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ABO_MEDIATHEQUE.id]


class AboPratiqueArtModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ABO_PRATIQUE_ART.id]


class AchatInstrumentModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ACHAT_INSTRUMENT.id]


class CarteCineIllimiteModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.CARTE_CINE_ILLIMITE.id]


class CarteCineUultiseancesModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.CARTE_CINE_MULTISEANCES.id]


class CarteJeunesModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.CARTE_JEUNES.id]


class CarteMuseeModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.CARTE_MUSEE.id]


class EscapeGameModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.ESCAPE_GAME.id]


class LivreAudioPhysiqueModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.LIVRE_AUDIO_PHYSIQUE.id]


class LocationInstrumentModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.LOCATION_INSTRUMENT.id]


class MaterielArtCreatifModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.MATERIEL_ART_CREATIF.id]


class PartitionModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.PARTITION.id]


class SupportPhysiqueFilmModel(ThingsBaseModel):
    subcategory_id: Literal[subcategories.SUPPORT_PHYSIQUE_FILM.id]
