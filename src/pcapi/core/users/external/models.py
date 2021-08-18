from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pcapi.core.users.models import DomainsCredit


@dataclass
class UserAttributes:
    booking_categories: list[str]
    date_created: datetime
    date_of_birth: datetime
    departement_code: Optional[str]
    deposit_expiration_date: Optional[datetime]
    domains_credit: Optional[DomainsCredit]
    first_name: Optional[str]
    is_beneficiary: bool
    last_booking_date: Optional[datetime]
    last_name: Optional[str]
    marketing_push_subscription: bool
    postal_code: Optional[str]
    products_use_date: dict
