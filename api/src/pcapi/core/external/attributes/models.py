from dataclasses import dataclass
import datetime
from decimal import Decimal
import typing

from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models


@dataclass
class UserAttributes:
    age: int | None
    booking_categories: list[str]
    booking_count: int  # count non-canceled bookings from user
    booking_subcategories: list[str]
    booking_venues_count: int  # count unique venues in which user has made at least one non-canceled booking
    city: str | None
    date_created: datetime.datetime
    date_of_birth: datetime.datetime | None
    departement_code: str | None
    deposits_count: int  # number of granted deposits, e.g. 2 if a beneficiary got Pass 15-17 and Pass 18
    deposit_activation_date: datetime.datetime | None
    deposit_expiration_date: datetime.datetime | None
    domains_credit: users_models.DomainsCredit | None
    eligibility: users_models.EligibilityType | None
    first_name: str | None
    has_completed_id_check: bool
    user_id: int
    is_active: bool  # Added for Zendesk
    is_beneficiary: bool
    is_current_beneficiary: bool  # Beneficiary with a non-expired remaining credit
    is_former_beneficiary: bool  # Beneficiary whose last possible credit is definitely expired or spent
    is_eligible: bool
    is_email_validated: bool | None  # nullable in user table
    is_phone_validated: bool  # Added for Zendesk
    is_pro: bool
    last_booking_date: datetime.datetime | None
    last_favorite_creation_date: datetime.datetime | None
    last_name: str | None
    last_visit_date: datetime.datetime | None
    marketing_email_subscription: bool
    marketing_push_subscription: bool
    most_booked_subcategory: str | None  # Single subcategory most frequently booked by the user
    most_booked_movie_genre: str | None
    most_booked_music_type: str | None
    most_favorite_offer_subcategories: list[str] | None
    phone_number: str | None  # Added for Zendesk, type: ignore [arg-type]
    postal_code: str | None
    products_use_date: dict
    roles: list[str]
    suspension_date: datetime.datetime | None  # Added for Zendesk
    suspension_reason: users_constants.SuspensionReason | None  # Added for Zendesk
    # Specific for Dec 2022 emailing campaign:
    amount_spent_2022: Decimal | typing.Literal[0]  # Amount of credit spent in year 2022 (non-canceled offers)
    first_booked_offer_2022: str | None  # First booked offer name in 2022 (non-canceled)
    last_booked_offer_2022: str | None  # Last booked offer name in 2022 (non-canceled)


@dataclass
class ProAttributes:
    # Attributes always set:
    is_pro: bool  # Always True
    is_user_email: bool  # Email address is set at least for a user account
    is_booking_email: bool  # Email address is set as bookingEmail for at least one active venue
    marketing_email_subscription: bool
    offerers_names: typing.Iterable[str]  # All active offerers associated with user account or bookingEmail
    offerers_tags: typing.Iterable[str]  # Cumulative tags on all active offerers
    venues_ids: typing.Iterable[int]  # All active venues ids related to email (from user account or bookingEmail)
    venues_names: typing.Iterable[str]  # Distinct names of all these venues
    venues_types: typing.Iterable[str]  # Distinct types of all these venues
    venues_labels: typing.Iterable[str]  # Distinct labels of all these venues
    departement_code: typing.Iterable[
        str
    ]  # Distinct department codes of all these venues; keep same name as UserAttributes
    postal_code: typing.Iterable[str]  # Distinct postal codes of all these venues; keep same name as UserAttributes

    # Attributes set when is_user_email is True:
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    user_is_attached: bool | None = None  # User is attached to at least one active offerer, he is not the creator
    user_is_creator: bool | None = None  # User is the creator of at least one active offerer
    is_eac: bool | None = None

    # Attributes set when is_booking_email is True,
    # which only take venues in which contact email is set as bookingEmail into account:
    dms_application_submitted: bool | None = None  # At last one bank info is waiting for approval in DMS in venues
    dms_application_approved: bool | None = None  # All venues have bank information approved
    isVirtual: bool | None = None  # At least one venue is virtual
    isPermanent: bool | None = None  # At least one venue is permanent
    has_offers: bool | None = None  # At least one venue has at least one active offer
    has_bookings: bool | None = None  # At least one venue has at least one booking not canceled, at least once
    has_collective_offers: bool | None = False  # At list one collective offer or collective offer template active


@dataclass
class BookingsAttributes:
    """Attributes computed from bookings (values returned by get_bookings_categories_and_subcategories)"""

    booking_categories: list[str]
    booking_subcategories: list[str]
    most_booked_subcategory: str | None = None
    most_booked_movie_genre: str | None = None
    most_booked_music_type: str | None = None
