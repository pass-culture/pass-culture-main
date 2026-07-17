import typing

from pydantic import Field
from pydantic import RootModel
from pydantic import field_validator

from pcapi.core.finance.utils import to_cents
from pcapi.routes.serialization import HttpBodyModel


class OfferImageResponse(HttpBodyModel):
    url: str
    credit: str | None


class OfferVenueResponse(HttpBodyModel):
    id: int
    publicName: str = Field(alias="commonName")


class OfferStockResponse(HttpBodyModel):
    id: int
    price: int

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, price: typing.Any) -> int:
        return to_cents(price)


class OfferResponse(HttpBodyModel):
    id: int
    name: str
    venue: OfferVenueResponse
    image: OfferImageResponse | None
    stocks: list[OfferStockResponse] = Field(validation_alias="bookableStocks")


class OffersResponse(RootModel):
    root: list[OfferResponse]
