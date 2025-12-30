from typing import Literal

from pcapi.core.categories import subcategories

from .unselectable import UnselectableBaseModel
from . import shared


class ActivationEventModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.ACTIVATION_EVENT.id]


class CaptationMusiqueModel(UnselectableBaseModel):
    subcategory_id: Literal[subcategories.CAPTATION_MUSIQUE.id]
    extra_data: shared.ExtraDataPerformedMusic | None = None


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
