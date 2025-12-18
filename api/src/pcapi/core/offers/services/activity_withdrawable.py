from typing import Literal

from pcapi.core.categories import subcategories

from . import shared
from .activity import ActivityBaseModel


# class AboSpectacleModel(ActivityBaseModel):
    # subcategoryId: Literal[subcategories.ABO_SPECTACLE.id]
    # extra_data: shared.ShowExtraData

class SpectacleRepresentationModel(Mandatory):
    subcategoryId: Literal[subcategories.SPECTACLE_REPRESENTATION.id]


class FestivalSpectacleModel(Mandatory):
    subcategoryId: Literal[subcategories.FESTIVAL_SPECTACLE.id]


class FestivalArtVisuelModel(Mandatory):
    subcategoryId: Literal[subcategories.FESTIVAL_ART_VISUEL.id]


class ConcertModel(Mandatory):
    subcategoryId: Literal[subcategories.CONCERT.id]


class FestivalMusiqueModel(Mandatory):
    subcategoryId: Literal[subcategories.FESTIVAL_MUSIQUE.id]


class EvenementMusiqueModel(Mandatory):
    subcategoryId: Literal[subcategories.EVENEMENT_MUSIQUE.id]



