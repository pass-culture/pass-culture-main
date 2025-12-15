from typing import Literal

from . import shared
from .base import Base


class UnselectableBaseModel(Base):
    pass


class ActivationEventModel(UnselectableBaseModel):
    subcategory_id: Literal["ACTIVATION_EVENT"]


class CaptationMusiqueModel(UnselectableBaseModel):
    subcategory_id: Literal["CAPTATION_MUSIQUE"]
    extra_data: shared.ExtraDataMusic


class OeuvreArtModel(UnselectableBaseModel):
    subcategory_id: Literal["OEUVRE_ART"]


class BonAchatInstrumentModel(UnselectableBaseModel):
    subcategory_id: Literal["BON_ACHAT_INSTRUMENT"]


class ActivationThingModel(UnselectableBaseModel):
    subcategory_id: Literal["ACTIVATION_THING"]


class AboLudothequeModel(UnselectableBaseModel):
    subcategory_id: Literal["ABO_LUDOTHEQUE"]


class JeuSupportPhysiqueModel(UnselectableBaseModel):
    subcategory_id: Literal["JEU_SUPPORT_PHYSIQUE"]


class DecouverteMetiersModel(UnselectableBaseModel):
    subcategory_id: Literal["DECOUVERTE_METIERS"]
    extra_data: shared.ExtraDataSpeaker
