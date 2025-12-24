from typing import Literal

from pcapi.core.categories import subcategories

from .unselectable import UnselectableBaseModel


class ActivationEventModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.ACTIVATION_EVENT.id]


class CaptationMusiqueModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.CAPTATION_MUSIQUE.id]


class OeuvreArtModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.OEUVRE_ART.id]


class BonAchatInstrumentModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.BON_ACHAT_INSTRUMENT.id]


class ActivationThingModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.ACTIVATION_THING.id]


class AboLudothequeModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.ABO_LUDOTHEQUE.id]


class JeuSupportPhysiqueModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.JEU_SUPPORT_PHYSIQUE.id]


class DecouverteMetiersModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.DECOUVERTE_METIERS.id]
