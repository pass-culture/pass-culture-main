from typing import Literal

from pydantic import HttpUrl

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


class ActivityOnline(ActivityBaseModel):
    url: HttpUrl


class LivestreamMusiqueModel(ActivityOnline):
    subcategory_id: Literal[subcategories.LIVESTREAM_MUSIQUE.id]
    extra_data: shared.ExtraDataMusic


class RencontreEnLigneModel(ActivityOnline):
    subcategory_id: Literal[subcategories.RENCONTRE_EN_LIGNE.id]
    extra_data: shared.ExtraDataSpeaker


class LivestreamPratiqueArtistiqueModel(ActivityOnline):
    subcategory_id: Literal[subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id]
