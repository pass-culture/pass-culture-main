from typing import Literal

import pydantic as pydantic_v2

from pcapi.core.categories import subcategories

from . import shared
from .digital import DigitalBaseModel


class DigitalShowModel(DigitalBaseModel):
    extra_data: shared.ShowExtraData | None
    model_config = pydantic_v2.ConfigDict(extra="forbid")


class SpectacleEnregistreModel(DigitalShowModel):
    subcategoryId: Literal[subcategories.SPECTACLE_ENREGISTRE.id]


class SpectacleVenteDistanceModel(DigitalShowModel):
    subcategoryId: Literal[subcategories.SPECTACLE_VENTE_DISTANCE.id]
