from typing import Literal

import pydantic as pydantic_v2
from pydantic import AfterValidator
from typing_extensions import Annotated

from pcapi.core.categories import subcategories

from .shared import Venue
from .shared import VenueTypeCode
from .things import ThingsBaseModel


def is_record_store(venue: Venue):
    return venue.code != VenueTypeCode.RECORD_STORE


class Product(pydantic_v2.BaseModel):
    id: int


class ExtraData(pydantic_v2.BaseModel):
    ean: str
    model_config = pydantic_v2.ConfigDict(extra="ignore")


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int


class ThingsWithEan(ThingsBaseModel):
    productId: int | None = None
    extraData: ExtraData | None = None

    provider_data: ProviderData | None = None


class LivrePapierModel(ThingsWithEan):
    subcategoryId: Literal[subcategories.LIVRE_PAPIER.id]


class VinyleModel(ThingsWithEan):
    subcategoryId: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id]


class CDModel(ThingsWithEan):
    subcategoryId: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id]
    product: Product
    venue: Annotated[Venue, AfterValidator(is_record_store)]
