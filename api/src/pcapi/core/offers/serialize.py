import dataclasses
from datetime import datetime
import enum
from typing import Any

from pydantic.v1 import EmailStr
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator

from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre collective" if offer_is_educational else "offre grand public"


class CollectiveOfferType(enum.Enum):
    offer = "offer"
    template = "template"


@dataclasses.dataclass
class StocksStats:
    oldest_stock: datetime | None
    newest_stock: datetime | None
    stock_count: int | None
    remaining_quantity: int | None


class PostDraftOfferBodyModel(BaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None = None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchDraftOfferBodyModel(BaseModel):
    name: str | None = None
    description: str | None = None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchDraftOfferDetailsBodyModel(BaseModel):
    audio_disability_compliant: bool | None = None
    mental_disability_compliant: bool | None = None
    motor_disability_compliant: bool | None = None
    visual_disability_compliant: bool | None = None
    booking_contact: EmailStr | None = None
    booking_email: EmailStr | None = None
    duration_minutes: int | None = None
    external_ticket_office_url: HttpUrl | None = None
    extra_data: Any = None
    is_duo: bool | None = None
    withdrawal_delay: int | None = None
    withdrawal_details: str | None = None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None = None

    # is_national must be placed after url so that the validator
    # can access the url field in the dict of values
    # (which contains only previously validated fields)
    is_national: bool | None = None
    should_send_mail: bool | None = None

    @validator("is_duo")
    def validate_is_duo(cls, is_duo: bool | None) -> bool:
        return bool(is_duo)

    @validator("is_national")
    def validate_is_national(cls, is_national: bool | None, values: dict) -> bool:
        url = values.get("url")
        is_national = True if url else bool(is_national)
        return is_national

    @validator("withdrawal_type")
    def validate_withdrawal_type(
        cls, withdrawal_type: offers_models.WithdrawalTypeEnum
    ) -> offers_models.WithdrawalTypeEnum:
        if withdrawal_type == offers_models.WithdrawalTypeEnum.IN_APP:
            raise ValueError("Withdrawal type cannot be in_app for manually created offers")
        return withdrawal_type

    @validator("should_send_mail")
    def validate_should_send_mail(cls, should_send_mail: bool | None) -> bool:
        return bool(should_send_mail)

    class Config:
        alias_generator = to_camel
        extra = "forbid"
