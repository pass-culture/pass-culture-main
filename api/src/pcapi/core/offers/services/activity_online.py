from typing import Literal

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


class ActivityOnline(ActivityBaseModel):
    extra_data: shared.ShowExtraData | None


class LivestreamMusiqueModel(ActivityOnline):
    subcategoryId: Literal[subcategories.LIVESTREAM_MUSIQUE.id]


class RencontreEnLigneModel(ActivityOnline):
    subcategoryId: Literal[subcategories.RENCONTRE_EN_LIGNE.id]


class LivestreamPratiqueArtistiqueModel(ActivityOnline):
    subcategoryId: Literal[subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id]
