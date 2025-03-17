import typing

from pydantic.v1 import EmailStr
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.schemas import SchemasBaseModel
from pcapi.serialization.utils import to_camel
from pcapi.validation.routes.offers import check_offer_name_length_is_valid

from .validation import check_offer_subcategory_is_valid


class CreateOffer(SchemasBaseModel):
    name: str
    subcategory_id: str
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool

    booking_contact: EmailStr | None
    booking_email: EmailStr | None
    description: str | None
    duration_minutes: int | None
    external_ticket_office_url: HttpUrl | None
    extra_data: typing.Any
    id_at_provider: str | None
    is_duo: bool | None
    url: HttpUrl | None
    withdrawal_delay: int | None
    withdrawal_details: str | None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None

    # is_national must be placed after url so that the validator
    # can access the url field in the dict of values
    # (which contains only previously validated fields)
    is_national: bool | None

    @validator("is_duo")
    def validate_is_duo(cls, is_duo: bool | None) -> bool:
        return bool(is_duo)

    @validator("is_national")
    def validate_is_national(cls, is_national: bool | None, values: dict) -> bool:
        url = values.get("url")
        is_national = True if url else bool(is_national)
        return is_national

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CreateDraftOffer(SchemasBaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None
    url: HttpUrl | None
    extra_data: typing.Any
    duration_minutes: int | None
    product_id: int | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        arbitrary_types_allowed = True
        alias_generator = to_camel
        extra = "forbid"


class UpdateOffer(SchemasBaseModel):
    name: str | None
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    address: offerers_schemas.AddressBodyModel | None
    booking_contact: EmailStr | None
    booking_email: EmailStr | None
    description: str | None
    duration_minutes: int | None
    external_ticket_office_url: HttpUrl | None
    extra_data: typing.Any
    id_at_provider: str | None
    is_duo: bool | None
    offerer_address: offerers_models.OffererAddress | None
    url: HttpUrl | None
    withdrawal_delay: int | None
    withdrawal_details: str | None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None

    is_active: bool | None

    # is_national must be placed after url so that the validator
    # can access the url field in the dict of values
    # (which contains only previously validated fields)
    is_national: bool | None

    should_send_mail: bool | None

    @validator("is_duo")
    def validate_is_duo(cls, is_duo: bool | None) -> bool:
        return bool(is_duo)

    @validator("is_national")
    def validate_is_national(cls, is_national: bool | None, values: dict) -> bool:
        url = values.get("url")
        is_national = True if url else bool(is_national)
        return is_national

    class Config:
        arbitrary_types_allowed = True
        alias_generator = to_camel
        extra = "forbid"


class UpdateDraftOffer(SchemasBaseModel):
    name: str | None
    subcategory_id: str | None
    url: HttpUrl | None
    description: str | None
    extra_data: dict[str, typing.Any] | None
    duration_minutes: int | None

    @validator("subcategory_id", pre=True)
    def validate_subcategory_id(cls, subcategory_id: str, values: dict) -> str:
        check_offer_subcategory_is_valid(subcategory_id)
        return subcategory_id

    class Config:
        alias_generator = to_camel
        extra = "forbid"
