import datetime
from datetime import date
from typing import Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from pydantic.class_validators import validator
from pydantic.fields import Field
from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users import constants as users_constants
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.api import needs_to_validate_phone
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.routes.native.utils import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date

from . import BaseModel


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: date
    marketing_email_subscription: Optional[bool] = False
    token: str
    postal_code: Optional[str] = None

    class Config:
        alias_generator = to_camel


class CulturalSurveyRequest(BaseModel):
    needs_to_fill_cultural_survey: bool
    cultural_survey_id: Optional[UUID]

    class Config:
        alias_generator = to_camel


class Expense(BaseModel):
    domain: ExpenseDomain
    current: int
    limit: int

    _convert_current = validator("current", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_limit = validator("limit", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True


class NotificationSubscriptions(BaseModel):
    marketing_email: bool
    marketing_push: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class Credit(BaseModel):
    initial: int
    remaining: int

    _convert_initial = validator("initial", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_remaining = validator("remaining", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True


class DomainsCredit(BaseModel):
    all: Credit
    digital: Optional[Credit]
    physical: Optional[Credit]

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    id: int
    booked_offers: dict[str, int]
    domains_credit: Optional[DomainsCredit]
    dateOfBirth: Optional[datetime.date]
    deposit_expiration_date: Optional[datetime.datetime]
    deposit_version: Optional[int]
    eligibility_end_datetime: Optional[datetime.datetime]
    eligibility_start_datetime: Optional[datetime.datetime]
    email: str
    firstName: Optional[str]
    hasCompletedIdCheck: Optional[bool]
    lastName: Optional[str]
    subscriptions: NotificationSubscriptions  # if we send user.notification_subscriptions, pydantic will take the column and not the property
    isBeneficiary: bool
    phoneNumber: Optional[str]
    publicName: Optional[str] = Field(None, alias="pseudo")
    needsToFillCulturalSurvey: bool
    show_eligible_card: bool
    needs_to_validate_phone: bool

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: format_into_utc_date}

    @validator("publicName", pre=True)
    def format_public_name(cls, publicName: str) -> Optional[str]:  # pylint: disable=no-self-argument
        return publicName if publicName != VOID_PUBLIC_NAME else None

    @validator("firstName", pre=True)
    def format_first_name(cls, firstName: Optional[str]) -> Optional[str]:  # pylint: disable=no-self-argument
        return firstName if firstName != VOID_FIRST_NAME else None

    @staticmethod
    def _show_eligible_card(user: User) -> bool:
        return (
            relativedelta(user.dateCreated, user.dateOfBirth).years < users_constants.ELIGIBILITY_AGE
            and user.isBeneficiary is False
            and user.is_eligible
        )

    @staticmethod
    def _get_booked_offers(user: User) -> dict:
        not_cancelled_bookings = Booking.query.options(
            joinedload(Booking.stock).joinedload(Stock.offer).load_only(Offer.id)
        ).filter_by(userId=user.id, isCancelled=False)

        return {booking.stock.offer.id: booking.id for booking in not_cancelled_bookings}

    @classmethod
    def from_orm(cls, user: User):  # type: ignore
        user.show_eligible_card = cls._show_eligible_card(user)
        user.subscriptions = user.get_notification_subscriptions()
        user.domains_credit = get_domains_credit(user)
        user.booked_offers = cls._get_booked_offers(user)
        user.needs_to_validate_phone = needs_to_validate_phone(user)
        result = super().from_orm(user)
        result.needsToFillCulturalSurvey = False
        return result


class UserProfileUpdateRequest(BaseModel):
    subscriptions: Optional[NotificationSubscriptions]


class ResendEmailValidationRequest(BaseModel):
    email: str


class GetIdCheckTokenResponse(BaseModel):
    token: Optional[str]
    token_timestamp: Optional[datetime.datetime]


class ValidatePhoneNumberRequest(BaseModel):
    code: str


class SendPhoneValidationRequest(BaseModel):
    phoneNumber: Optional[str]
