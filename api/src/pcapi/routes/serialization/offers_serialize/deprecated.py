import typing

from pydantic.v1 import validator

from pcapi.core.offers import validation as offers_validation
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import address_serialize
from pcapi.serialization.utils import to_camel


class PostOfferBodyModel(BaseModel):
    audio_disability_compliant: bool
    description: str | None
    duration_minutes: int | None
    extra_data: dict[str, typing.Any] | None
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    name: str
    subcategory_id: str
    venue_id: int
    visual_disability_compliant: bool

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        offers_validation.check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"
