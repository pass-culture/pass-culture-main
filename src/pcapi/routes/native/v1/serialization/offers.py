from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field


class GetOfferOfferTypeResponse(BaseModel):
    appLabel: str = Field(..., alias="label")
    value: str

    class Config:
        allow_population_by_field_name = True


class GetOfferManaginOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GetOfferVenueResponse(BaseModel):
    city: Optional[str]
    managingOfferer: GetOfferManaginOffererResponse = Field(..., alias="offerer")
    name: str
    publicName: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class GetOfferResponse(BaseModel):
    id: int
    isDuo: bool
    name: str
    offerType: GetOfferOfferTypeResponse = Field(..., alias="category")
    thumbUrl: Optional[str] = Field(None, alias="imageUrl")
    venue: GetOfferVenueResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
