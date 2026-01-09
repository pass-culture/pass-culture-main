from typing import Literal

from pcapi.core.categories import subcategories

from . import shared
from .digital import DigitalBaseModel


class DigitalShowModel(DigitalBaseModel):
    extra_data: shared.ExtraDataShow | None


class SpectacleEnregistreModel(DigitalShowModel):
    subcategory_id: Literal[subcategories.SPECTACLE_ENREGISTRE.id]


class SpectacleVenteDistanceModel(DigitalShowModel):
    subcategory_id: Literal[subcategories.SPECTACLE_VENTE_DISTANCE.id]
