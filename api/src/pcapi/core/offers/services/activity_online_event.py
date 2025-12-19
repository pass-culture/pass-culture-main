from typing import Literal

from pydantic import HttpUrl

from pcapi.core.categories import subcategories

from .activity import ActivityBaseModel


# NOTICE(jbaudet - 12/2025): can be an event
class LivestreamEvenementModel(ActivityBaseModel):
    url: HttpUrl
    subcategory_id: Literal[subcategories.LIVESTREAM_EVENEMENT.id]
