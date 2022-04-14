from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from typing import Optional

from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType


@dataclass
class UserAttributes:
    booking_categories: list[str]
    booking_count: int
    booking_subcategories: list[str]
    city: Optional[str]
    date_created: datetime
    date_of_birth: datetime
    departement_code: Optional[str]
    deposit_activation_date: Optional[datetime]
    deposit_expiration_date: Optional[datetime]
    domains_credit: Optional[DomainsCredit]
    eligibility: Optional[EligibilityType]
    first_name: Optional[str]
    has_completed_id_check: bool
    user_id: int
    is_active: bool  # Added for Zendesk
    is_beneficiary: bool
    is_eligible: bool
    is_email_validated: bool
    is_phone_validated: bool  # Added for Zendesk
    is_pro: bool
    last_booking_date: Optional[datetime]
    last_favorite_creation_date: Optional[datetime]
    last_name: Optional[str]
    last_visit_date: Optional[datetime]
    marketing_email_subscription: bool
    marketing_push_subscription: bool
    phone_number: Optional[str]  # Added for Zendesk
    postal_code: Optional[str]
    products_use_date: dict
    roles: list[str]
    suspension_date: Optional[datetime]  # Added for Zendesk
    suspension_reason: Optional[str]  # Added for Zendesk


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
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_is_attached: Optional[bool] = None  # User is attached to at least one active offerer, he is not the creator
    user_is_creator: Optional[bool] = None  # User is the creator of at least one active offerer

    # Attributes set when is_booking_email is True,
    # which only take venues in which contact email is set as bookingEmail into account:
    dms_application_submitted: Optional[bool] = None  # At last one bank info is waiting for approval in DMS in venues
    dms_application_approved: Optional[bool] = None  # All venues have bank information approved
    isVirtual: Optional[bool] = None  # At least one venue is virtual
    isPermanent: Optional[bool] = None  # At least one venue is permanent
    has_offers: Optional[bool] = None  # At least one venue has at least one active offer
    has_bookings: Optional[bool] = None  # At least one venue has at least one booking not canceled, at least once
