from datetime import datetime
from decimal import Decimal

from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit


common_user_attributes = UserAttributes(
    booking_count=4,
    booking_categories=["CINEMA", "LIVRE"],
    booking_subcategories=["ABO_LIVRE_NUMERIQUE", "CARTE_CINE_ILLIMITE", "CINE_PLEIN_AIR"],
    date_created=datetime(2021, 2, 6),
    date_of_birth=datetime(2003, 5, 6),
    departement_code="12",
    deposit_activation_date=None,
    deposit_expiration_date=None,
    domains_credit=DomainsCredit(
        all=Credit(initial=Decimal("500"), remaining=Decimal("480.00")),
        digital=Credit(initial=Decimal("200"), remaining=Decimal("200")),
        physical=Credit(initial=200, remaining=Decimal("180.00")),
    ),
    first_name="First name",
    has_completed_id_check=True,
    is_beneficiary=True,
    is_eligible=True,
    is_email_validated=True,
    is_pro=False,
    last_booking_date=datetime(2021, 5, 6),
    last_favorite_creation_date=None,
    last_name="Last name",
    last_visit_date=None,
    marketing_email_subscription=True,
    marketing_push_subscription=True,
    postal_code=None,
    products_use_date={"product_brut_x_use": datetime(2021, 5, 6)},
    user_id=1,
)
