from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic.class_validators import validator

from pcapi.domain.password import check_password_strength
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.serialization.utils import validate_not_empty_string_when_provided
from pcapi.serialization.utils import validate_phone_number_format
from pcapi.utils.date import format_into_utc_date


class PatchUserBodyModel(BaseModel):
    cultural_survey_id: Optional[str]
    cultural_survey_filled_date: Optional[str]
    department_code: Optional[str] = Field(None, alias="departementCode")
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    needs_to_fill_cultural_survey: Optional[bool]
    phone_number: Optional[str]
    postal_code: Optional[str]
    public_name: Optional[str]
    has_seen_tutorials: Optional[bool]

    _validate_first_name = validate_not_empty_string_when_provided("first_name")
    _validate_last_name = validate_not_empty_string_when_provided("last_name")
    _validate_email = validate_not_empty_string_when_provided("email")
    _validate_phone_number = validate_not_empty_string_when_provided("phone_number")
    _validate_phone_number_format = validate_phone_number_format("phone_number")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchUserResponseModel(BaseModel):
    id: str
    email: EmailStr
    publicName: str
    postalCode: str
    phoneNumber: Optional[str]
    departementCode: str
    activity: Optional[str]
    address: Optional[str]
    isBeneficiary: bool
    city: Optional[str]
    civility: Optional[str]
    dateCreated: datetime
    dateOfBirth: Optional[datetime]
    firstName: Optional[str]
    hasOffers: bool
    hasPhysicalVenues: bool
    isAdmin: bool
    lastConnectionDate: Optional[datetime]
    lastName: Optional[str]
    needsToFillCulturalSurvey: bool

    _normalize_id = humanize_field("id")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


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
    departementCode: str
    email: str
    firstName: Optional[str]
    hasAllowedRecommendations: bool
    hasOffers: Optional[bool]
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

    _normalize_id = humanize_field("id")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
