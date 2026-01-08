import typing
from typing import Literal

import pydantic as pydantic_v2

from pcapi.core.categories import subcategories

from . import shared
from .things import ThingsBaseModel


class Product(pydantic_v2.BaseModel):
    id: int


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int


class ThingsWithEan(ThingsBaseModel):
    product: Product | None = None
    provider_data: ProviderData | None = None


class LivrePapierModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.LIVRE_PAPIER.id]
    extra_data: shared.ExtraDataBookWithGtl


class SupportPhysiqueMusiqueVinyleModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id]
    extra_data: shared.ExtraDataMusicWithEan


class SupportPhysiqueMusiqueCDModel(ThingsWithEan):
    subcategory_id: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id]
    venue: shared.Venue
    extra_data: shared.ExtraDataMusicWithEan

    @pydantic_v2.model_validator(mode='after')
    def check_has_product_if_from_record_store(self) -> typing.Self:
        if self.venue.code == shared.VenueTypeCode.RECORD_STORE and not self.product:
            raise ValueError('Record store implies that a product is set')
        return self
