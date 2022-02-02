from datetime import datetime
from decimal import Decimal

from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.users.external.models import ProAttributes
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
    eligibility="age-18",
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
    roles=["BENEFICIARY"],
)


common_pro_attributes = ProAttributes(
    is_pro=True,
    is_user_email=True,
    is_booking_email=True,
    offerer_name=["Offerer Name 1", "Offerer Name 2"],
    user_id=2,
    first_name="First name",
    last_name="Last name",
    marketing_email_subscription=True,
    user_is_attached=False,
    user_is_creator=True,
    venue_count=2,
    venue_name=["Venue Name 1", "Venue Name 2"],
    venue_type=[VenueTypeCode.BOOKSTORE.name, VenueTypeCode.MOVIE.name],
    venue_label=["Venue Label"],
    departement_code=["04,06"],
    dms_application_submitted=False,
    dms_application_approved=True,
    isVirtual=False,
    isPermanent=True,
    has_offers=True,
    has_bookings=True,
)
