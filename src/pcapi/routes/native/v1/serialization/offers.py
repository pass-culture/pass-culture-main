from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field


class OfferCategoryResponse(BaseModel):
    appLabel: str = Field(..., alias="label")
    value: str

    class Config:
        allow_population_by_field_name = True


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferVenueResponse(BaseModel):
    city: Optional[str]
    managingOfferer: OfferOffererResponse = Field(..., alias="offerer")
    name: str
    publicName: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OfferResponse(BaseModel):
    id: int
    isDuo: bool
    name: str
    offerType: OfferCategoryResponse = Field(..., alias="category")
    thumbUrl: Optional[str] = Field(None, alias="imageUrl")
    venue: OfferVenueResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
