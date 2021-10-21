from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic.class_validators import validator

from pcapi.core.users.models import UserRole
from pcapi.domain.password import check_password_strength
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.serialization.utils import validate_not_empty_string_when_provided
from pcapi.serialization.utils import validate_phone_number_format
from pcapi.utils.date import format_into_utc_date


class PatchProUserBodyModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]

    _validate_first_name = validate_not_empty_string_when_provided("first_name")
    _validate_last_name = validate_not_empty_string_when_provided("last_name")
    _validate_email = validate_not_empty_string_when_provided("email")
    _validate_phone_number = validate_not_empty_string_when_provided("phone_number")
    _validate_phone_number_format = validate_phone_number_format("phone_number")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchProUserResponseModel(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    email: EmailStr
    phoneNumber: Optional[str]

    class Config:
        orm_mode = True
        alias_generator = to_camel


class ProUserCreationBodyModel(BaseModel):
    address: Optional[str]
    city: Optional[str]
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    name: Optional[str]
    password: str
    phone_number: str
    postal_code: Optional[str]
    public_name: Optional[str]
    siren: Optional[str]
    contact_ok: Optional[bool]

    @validator("password")
    def validate_password_strength(cls, password: str) -> str:  # typing: ignore # pylint: disable=no-self-argument
        check_password_strength("password", password)
        return password

    @validator("contact_ok", pre=True, always=True)
    def cast_contact_ok_to_bool(  # typing: ignore # pylint: disable=no-self-argument
        cls, contact_ok: Optional[bool]
    ) -> bool:
        return bool(contact_ok)

    _validate_phone_number_format = validate_phone_number_format("phone_number")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class LoginUserBodyModel(BaseModel):
    identifier: str
    password: str


class SharedLoginUserResponseModel(BaseModel):
    activity: Optional[str]
    address: Optional[str]
    city: Optional[str]
    civility: Optional[str]
    dateCreated: datetime
    dateOfBirth: Optional[datetime]
    departementCode: Optional[str]
    email: str
    firstName: Optional[str]
    hasPhysicalVenues: Optional[bool]
    hasSeenProTutorials: Optional[bool]
    id: str
    isAdmin: bool
    isBeneficiary: bool
    isEmailValidated: bool
    lastConnectionDate: Optional[datetime]
    lastName: Optional[str]
    needsToFillCulturalSurvey: Optional[bool]
    phoneNumber: Optional[str]
    postalCode: Optional[str]
    publicName: Optional[str]
    roles: list[UserRole]

    _normalize_id = humanize_field("id")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True

    @classmethod
    def from_orm(cls, user):
        result = super().from_orm(user)
        result.isBeneficiary = user.is_beneficiary
        return result
