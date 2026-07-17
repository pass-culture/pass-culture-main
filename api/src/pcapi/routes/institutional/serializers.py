from typing import Any

from pydantic import Field
from pydantic import RootModel
from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict

from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.price import convert_to_cent


class OfferImageResponse(HttpBodyModel):
    url: str
    credit: str | None = None


class OfferVenueResponse(HttpBodyModel):
    id: int
    publicName: str = Field(alias="commonName")


class OfferStockResponse(HttpBodyModel):
    id: int
    price: int

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)


class ActiveStockGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "stocks":
            return [OfferStockResponse.from_orm(stock) for stock in self._obj.stocks if stock.isBookable]
        return super().get(key, default)


class OfferResponse(HttpBodyModel):
    id: int
    name: str
    venue: OfferVenueResponse
    image: OfferImageResponse | None = None
    stocks: list[OfferStockResponse]

    class Config:
        getter_dict = ActiveStockGetterDict


class OffersResponse(RootModel):
    root: list[OfferResponse]
