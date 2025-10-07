import typing

from pydantic.v1 import EmailStr
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator

from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class PostOfferBodyModel(BaseModel):
    address: offerers_schemas.AddressBodyModel | None
    audio_disability_compliant: bool
    booking_contact: EmailStr | None
    booking_email: EmailStr | None
    description: str | None
    duration_minutes: int | None
    external_ticket_office_url: HttpUrl | None
    extra_data: dict[str, typing.Any] | None
    is_duo: bool | None
    is_national: bool | None
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    name: str
    subcategory_id: str
    url: HttpUrl | None
    venue_id: int
    visual_disability_compliant: bool
    withdrawal_delay: int | None
    withdrawal_details: str | None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    @validator("withdrawal_type")
    def validate_withdrawal_type(cls, value: offers_models.WithdrawalTypeEnum) -> offers_models.WithdrawalTypeEnum:
        if value == offers_models.WithdrawalTypeEnum.IN_APP:
            raise ValueError("Withdrawal type cannot be in_app for manually created offers")
        return value

    class Config:
        alias_generator = to_camel
        extra = "forbid"
