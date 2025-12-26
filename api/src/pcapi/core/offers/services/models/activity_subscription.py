from typing import Literal

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


class AboSpectacleModel(ActivityBaseModel):
    subcategory_id: Literal[subcategories.ABO_SPECTACLE.id]
    extra_data: shared.ShowTypeModel
