from typing import Any

from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict

from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent


class OfferImageResponse(ConfiguredBaseModel):
    url: str
    credit: str | None


class OfferVenueResponse(ConfiguredBaseModel):
    id: int
    common_name: str | None


class OfferStockResponse(ConfiguredBaseModel):
    id: int
    price: int

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)


class ActiveStockGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "stocks":
            return [OfferStockResponse.from_orm(stock) for stock in self._obj.stocks if stock.isBookable]
        return super().get(key, default)


class OfferResponse(ConfiguredBaseModel):
    id: int
    name: str
    venue: OfferVenueResponse
    image: OfferImageResponse | None
    stocks: list[OfferStockResponse]

    class Config:
        getter_dict = ActiveStockGetterDict


class OffersResponse(ConfiguredBaseModel):
    __root__: list[OfferResponse]
