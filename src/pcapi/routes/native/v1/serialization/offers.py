from datetime import datetime
from decimal import Decimal
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field


class Coordinates(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


class OfferCategoryResponse(BaseModel):
    categoryType: str
    label: str
    name: str


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: Optional[datetime]
    price: Decimal

    class Config:
        orm_mode = True


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue):
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        return super().from_orm(venue)

    id: int
    address: Optional[str]
    city: Optional[str]
    managingOfferer: OfferOffererResponse = Field(..., alias="offerer")
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    coordinates: Coordinates

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OfferResponse(BaseModel):
    @classmethod
    def from_orm(cls, offer):
        offer.category = {
            "name": offer.offer_category,
            "label": offer.offerType["appLabel"],
            "categoryType": offer.category_type,
        }
        return super().from_orm(offer)

    id: int
    description: Optional[str]
    isDigital: bool
    isDuo: bool
    name: str
    category: OfferCategoryResponse
    bookableStocks: List[OfferStockResponse]
    thumbUrl: Optional[str] = Field(None, alias="imageUrl")
    venue: OfferVenueResponse
    withdrawalDetails: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
