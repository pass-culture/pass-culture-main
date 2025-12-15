from typing import Literal

from . import shared
from .base import Base
from .base import Typology


class ActivationEventModel(Base):
    subcategory_id: Literal["ACTIVATION_EVENT"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class CaptationMusiqueModel(Base):
    subcategory_id: Literal["CAPTATION_MUSIQUE"]
    extra_data: shared.ExtraDataMusic
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class OeuvreArtModel(Base):
    subcategory_id: Literal["OEUVRE_ART"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class BonAchatInstrumentModel(Base):
    subcategory_id: Literal["BON_ACHAT_INSTRUMENT"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class ActivationThingModel(Base):
    subcategory_id: Literal["ACTIVATION_THING"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class AboLudothequeModel(Base):
    subcategory_id: Literal["ABO_LUDOTHEQUE"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class JeuSupportPhysiqueModel(Base):
    subcategory_id: Literal["JEU_SUPPORT_PHYSIQUE"]
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED


class DecouverteMetiersModel(Base):
    subcategory_id: Literal["DECOUVERTE_METIERS"]
    extra_data: shared.ExtraDataSpeaker
    typology: Literal[Typology.CANNOT_BE_CREATED] = Typology.CANNOT_BE_CREATED
