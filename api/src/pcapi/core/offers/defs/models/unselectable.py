from typing import Literal

from .base import Base
from .shared import extra_data as shared_extra_data


class ActivationEventModel(Base):
    subcategory_id: Literal["ACTIVATION_EVENT"]


class CaptationMusiqueModel(Base):
    subcategory_id: Literal["CAPTATION_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic


class OeuvreArtModel(Base):
    subcategory_id: Literal["OEUVRE_ART"]


class BonAchatInstrumentModel(Base):
    subcategory_id: Literal["BON_ACHAT_INSTRUMENT"]


class ActivationThingModel(Base):
    subcategory_id: Literal["ACTIVATION_THING"]


class AboLudothequeModel(Base):
    subcategory_id: Literal["ABO_LUDOTHEQUE"]


class JeuSupportPhysiqueModel(Base):
    subcategory_id: Literal["JEU_SUPPORT_PHYSIQUE"]


class DecouverteMetiersModel(Base):
    subcategory_id: Literal["DECOUVERTE_METIERS"]
    extra_data: shared_extra_data.ExtraDataSpeaker
