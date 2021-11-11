from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType


@dataclass
class UserAttributes:
    booking_categories: list[str]
    booking_count: int
    booking_subcategories: list[str]
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
    is_beneficiary: bool
    is_eligible: bool
    is_email_validated: bool
    is_pro: bool
    last_booking_date: Optional[datetime]
    last_favorite_creation_date: Optional[datetime]
    last_name: Optional[str]
    last_visit_date: Optional[datetime]
    marketing_email_subscription: bool
    marketing_push_subscription: bool
    postal_code: Optional[str]
    products_use_date: dict
