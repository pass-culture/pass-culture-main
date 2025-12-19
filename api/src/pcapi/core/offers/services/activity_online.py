from typing import Literal

from pydantic import HttpUrl

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


class ActivityOnline(ActivityBaseModel):
    url: HttpUrl
    extra_data: shared.ShowExtraData | None


class LivestreamMusiqueModel(ActivityOnline):
    subcategory_id: Literal[subcategories.LIVESTREAM_MUSIQUE.id]


class RencontreEnLigneModel(ActivityOnline):
    subcategory_id: Literal[subcategories.RENCONTRE_EN_LIGNE.id]


class LivestreamPratiqueArtistiqueModel(ActivityOnline):
    subcategory_id: Literal[subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id]
