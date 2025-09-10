import typing

from pydantic.v1 import Field
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator

from pcapi.routes.serialization import BaseModel
from pcapi.serialization import utils as serialization_utils
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_video_url


OFFER_DESCRIPTION_MAX_LENGTH = 10_000


class PostDraftOfferBodyModel(BaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
    url: HttpUrl | None = None
    extra_data: typing.Any = None
    duration_minutes: int | None = None
    product_id: int | None
    # These props become mandatory when `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` feature flag is enabled.
    # They are optional here in order to not break the existing POST `/offers/drafts` route while both flows coexist.
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"


OFFER_DESCRIPTION_MAX_LENGTH = 10_000


class PatchDraftOfferBodyModel(BaseModel):
    name: str | None = None
    subcategory_id: str | None = None
    url: HttpUrl | None = None
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
    extra_data: dict[str, typing.Any] | None = None
    duration_minutes: int | None = None
    video_url: HttpUrl | None
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    @validator("video_url", pre=True)
    def clean_video_url(cls, v: str) -> str | None:
        if v == "":
            return None
        return v

    @validator("video_url")
    def validate_video_url(cls, video_url: HttpUrl, values: dict) -> str:
        check_video_url(video_url)
        return video_url

    @validator("subcategory_id", pre=True)
    def validate_subcategory_id(cls, subcategory_id: str, values: dict) -> str:
        from pcapi.core.offers.validation import check_offer_subcategory_is_valid

        check_offer_subcategory_is_valid(subcategory_id)
        return subcategory_id

    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"
