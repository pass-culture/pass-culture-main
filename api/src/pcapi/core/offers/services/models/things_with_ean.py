from typing import Literal

import pydantic as pydantic_v2
from pydantic import AfterValidator
from typing_extensions import Annotated

from pcapi.core.categories import subcategories

from .things import ThingsBaseModel

from . import shared


def is_record_store(venue: shared.Venue):
    return venue.code != shared.VenueTypeCode.RECORD_STORE


class Product(pydantic_v2.BaseModel):
    id: int


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int


class ThingsWithEan(ThingsBaseModel):
    productId: int | None = None
    provider_data: ProviderData | None = None


class LivrePapierModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.LIVRE_PAPIER.id]
    extra_data: shared.ExtraDataBookWithGtl


class SupportPhysiqueMusiqueVinyleModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id]
    extra_data: shared.ExtraDataMusicWithEan


class SupportPhysiqueMusiqueCDModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id]
    product: Product
    venue: Annotated[shared.Venue, AfterValidator(is_record_store)]
    extra_data: shared.ExtraDataMusicWithEan
