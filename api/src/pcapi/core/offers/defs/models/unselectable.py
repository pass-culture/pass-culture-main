from typing import Literal

from . import base
from .shared import extra_data as shared_extra_data


class ActivationEventModel(base.Base):
    subcategory_id: Literal["ACTIVATION_EVENT"]
    _typology: set[base.Typology] = {"activity", "unselectable"}


class CaptationMusiqueModel(base.Base):
    subcategory_id: Literal["CAPTATION_MUSIQUE"]
    extra_data: shared_extra_data.ExtraDataMusic
    _typology: set[base.Typology] = {"digital", "unselectable"}


class OeuvreArtModel(base.Base):
    subcategory_id: Literal["OEUVRE_ART"]
    _typology: set[base.Typology] = {"unselectable"}


class BonAchatInstrumentModel(base.Base):
    subcategory_id: Literal["BON_ACHAT_INSTRUMENT"]
    _typology: set[base.Typology] = {"unselectable"}


class ActivationThingModel(base.Base):
    subcategory_id: Literal["ACTIVATION_THING"]
    _typology: set[base.Typology] = {"unselectable"}


class AboLudothequeModel(base.Base):
    subcategory_id: Literal["ABO_LUDOTHEQUE"]
    _typology: set[base.Typology] = {"unselectable"}


class JeuSupportPhysiqueModel(base.Base):
    subcategory_id: Literal["JEU_SUPPORT_PHYSIQUE"]
    _typology: set[base.Typology] = {"unselectable"}


class DecouverteMetiersModel(base.Base):
    subcategory_id: Literal["DECOUVERTE_METIERS"]
    extra_data: shared_extra_data.ExtraDataSpeaker
    _typology: set[base.Typology] = {"activity", "unselectable"}
