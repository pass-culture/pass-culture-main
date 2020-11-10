from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


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



class UpdateMediationResponseModel(BaseModel):
    authorId: Optional[str]
    credit: Optional[str]
    dateCreated: Optional[datetime]
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: Optional[List[str]]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    lastProviderId: Optional[str]
    offerId: Optional[str]
    thumbCount: int
    thumbUrl: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_author_id = humanize_field("authorId")
    _humanize_id_at_providers = humanize_field("idAtProviders")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_offer_id = humanize_field("offerId")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True


class UpdateMediationBodyModel(BaseModel):
    isActive: bool
