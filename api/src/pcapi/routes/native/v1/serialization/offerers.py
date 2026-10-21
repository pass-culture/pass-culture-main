import datetime
import logging
import textwrap

import pydantic as pydantic_v2

from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


logger = logging.getLogger(__name__)


# TODO: Will be deleted in PR #24783 after native code deletion
class VenueProAdviceQuery(HttpQueryParamsModel):
    max_content_length: int | None = pydantic_v2.Field(default=None, gt=0)
    page: int = pydantic_v2.Field(default=1, gt=0)
    results_per_page: int = pydantic_v2.Field(default=20, gt=0)


# TODO: Will be deleted in PR #24783 after native code deletion
class VenueProAdvice(HttpBodyModel):
    author: str | None = None
    content: str
    offer_id: int
    offer_name: str
    offer_category_label: str
    offer_thumb_url: str | None = None
    publication_datetime: datetime.datetime

    @classmethod
    def build(cls, pro_advice: offers_models.ProAdvice, max_content_length: int | None) -> "VenueProAdvice":
        content = pro_advice.content
        if max_content_length:
            content = textwrap.shorten(content, width=max_content_length, placeholder="…")

        return cls(
            author=pro_advice.author,
            content=content,
            offer_id=pro_advice.offer.id,
            offer_name=pro_advice.offer.name,
            offer_category_label=pro_advice.offer.subcategory.app_label,
            offer_thumb_url=pro_advice.offer.thumbUrl,
            publication_datetime=pro_advice.updatedAt,
        )


# TODO: Will be deleted in PR #24783 after native code deletion
class VenueProAdvices(HttpBodyModel):
    pro_advices: list[VenueProAdvice]
    nb_results: int
