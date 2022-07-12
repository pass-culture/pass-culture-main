from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType


@dataclass
class UserAttributes:
    booking_categories: list[str]
    booking_count: int
    booking_subcategories: list[str]
    city: str | None
    date_created: datetime
    date_of_birth: datetime
    departement_code: str | None
    deposit_activation_date: datetime | None
    deposit_expiration_date: datetime | None
    domains_credit: DomainsCredit | None
    eligibility: EligibilityType | None
    first_name: str | None
    has_completed_id_check: bool
    user_id: int
    is_active: bool  # Added for Zendesk
    is_beneficiary: bool
    is_current_beneficiary: bool  # Beneficiary with a non-expired remaining credit
    is_former_beneficiary: bool  # Beneficiary which credit is expired or spent
    is_eligible: bool
    is_email_validated: bool
    is_phone_validated: bool  # Added for Zendesk
    is_pro: bool
    last_booking_date: datetime | None
    last_favorite_creation_date: datetime | None
    last_name: str | None
    last_visit_date: datetime | None
    marketing_email_subscription: bool
    marketing_push_subscription: bool
    most_booked_subcategory: str | None  # Single subcategory most frequently booked by the user
    phone_number: str | None  # Added for Zendesk
    postal_code: str | None
    products_use_date: dict
    roles: list[str]
    suspension_date: datetime | None  # Added for Zendesk
    suspension_reason: str | None  # Added for Zendesk


@dataclass
class ProAttributes:
    # Attributes always set:
    is_pro: bool  # Always True
    is_user_email: bool  # Email address is set at least for a user account
    is_booking_email: bool  # Email address is set as bookingEmail for at least one active venue
    marketing_email_subscription: bool
    offerers_names: Iterable[str]  # All active offerers associated with user account or bookingEmail
    venues_ids: Iterable[int]  # All active venues ids related to email (from user account or bookingEmail)
    venues_names: Iterable[str]  # Distinct names of all these venues
    venues_types: Iterable[str]  # Distinct types of all these venues
    venues_labels: Iterable[str]  # Distinct labels of all these venues
    departement_code: Iterable[str]  # Distinct department codes of all these venues; keep same name as UserAttributes
    postal_code: Iterable[str]  # Distinct postal codes of all these venues; keep same name as UserAttributes

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
