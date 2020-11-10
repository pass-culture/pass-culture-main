from typing import Optional

from pydantic import BaseModel, Field

from pcapi.serialization.utils import to_camel, dehumanize_field, humanize_field


class CreateMediationBodyModel(BaseModel):
    thumb_url: Optional[str]
    offerer_id: int
    offer_id: int
    credit: Optional[str]
    cropping_rect_x: Optional[float] = Field(None, alias="croppingRect[x]")
    cropping_rect_y: Optional[float] = Field(None, alias="croppingRect[y]")
    cropping_rect_height: Optional[float] = Field(None, alias="croppingRect[height]")

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel


class MediationResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetMediationResponseModel(BaseModel):
    thumb_url: Optional[str]
    offerer_id: int
    offer_id: int
    credit: Optional[str]
    cropping_rect_x: Optional[float] = Field(None, alias="croppingRect[x]")
    cropping_rect_y: Optional[float] = Field(None, alias="croppingRect[y]")
    cropping_rect_height: Optional[float] = Field(None, alias="croppingRect[height]")

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel
