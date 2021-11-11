from datetime import datetime
from decimal import Decimal

import pytest

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.external import TRACKED_PRODUCT_IDS
from pcapi.core.users.external import _get_bookings_categories_and_subcategories
from pcapi.core.users.external import _get_user_bookings
from pcapi.core.users.external import get_user_attributes
from pcapi.core.users.external import update_external_user
from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import UserRole
from pcapi.notifications.push import testing as batch_testing


MAX_BATCH_PARAMETER_SIZE = 30

pytestmark = pytest.mark.usefixtures("db_session")


def test_update_external_user():
    user = BeneficiaryGrant18Factory()
    IndividualBookingFactory(individualBooking__user=user)

    n_query_get_user = 1
    n_query_get_bookings = 1
    n_query_get_deposit = 1
    n_query_is_pro = 1
    n_query_get_last_favorite = 1

    with assert_num_queries(
        n_query_get_user + n_query_get_bookings + n_query_get_deposit + n_query_is_pro + n_query_get_last_favorite
    ):
        update_external_user(user)

    assert len(batch_testing.requests) == 1
    assert len(sendinblue_testing.sendinblue_requests) == 1


def test_update_external_pro_user():
    user = ProFactory()

    n_query_get_user = 1
    n_query_is_pro = 1

    with assert_num_queries(n_query_get_user + n_query_is_pro):
        update_external_user(user)

    assert len(batch_testing.requests) == 0
    assert len(sendinblue_testing.sendinblue_requests) == 1


def test_get_user_attributes():
    user = BeneficiaryGrant18Factory(deposit__version=1)
    offer = OfferFactory(product__id=list(TRACKED_PRODUCT_IDS.keys())[0])
    b1 = IndividualBookingFactory(individualBooking__user=user, amount=10, stock__offer=offer)
    b2 = IndividualBookingFactory(
        individualBooking__user=user, amount=10, dateUsed=datetime(2021, 5, 6), stock__offer=offer
    )
    IndividualBookingFactory(
        individualBooking__user=user, amount=100, status=BookingStatus.CANCELLED
    )  # should be ignored

    last_date_created = max(booking.dateCreated for booking in [b1, b2])

    n_query_get_user = 1
    n_query_get_bookings = 1
    n_query_get_deposit = 1
    n_query_is_pro = 1
    n_query_get_last_favorite = 1

    with assert_num_queries(
        n_query_get_user + n_query_get_bookings + n_query_get_deposit + n_query_is_pro + n_query_get_last_favorite
    ):
        attributes = get_user_attributes(user)

    assert attributes == UserAttributes(
        domains_credit=DomainsCredit(
            all=Credit(initial=Decimal("500"), remaining=Decimal("480.00")),
            digital=Credit(initial=Decimal("200"), remaining=Decimal("200")),
            physical=Credit(initial=200, remaining=Decimal("180.00")),
        ),
        booking_categories=["FILM"],
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code="75",
        deposit_expiration_date=user.deposit_expiration_date,
        eligibility=EligibilityType.AGE18,
        first_name="Jeanne",
        is_beneficiary=True,
        is_pro=False,
        last_booking_date=last_date_created,
        last_name="Doux",
        marketing_push_subscription=True,
        postal_code=None,
        products_use_date={"product_brut_x_use": datetime(2021, 5, 6, 0, 0)},
        booking_count=2,
        booking_subcategories=["SUPPORT_PHYSIQUE_FILM"],
        deposit_activation_date=user.deposit_activation_date,
        has_completed_id_check=None,
        user_id=user.id,
        is_eligible=True,
        is_email_validated=True,
        last_favorite_creation_date=None,
        last_visit_date=None,
        marketing_email_subscription=True,
        roles=[UserRole.BENEFICIARY],
    )


def test_get_bookings_categories_and_subcategories():
    user = BeneficiaryGrant18Factory()
    offer = OfferFactory(product__id=list(TRACKED_PRODUCT_IDS.keys())[0])

    assert _get_bookings_categories_and_subcategories(_get_user_bookings(user)) == ([], [])

    IndividualBookingFactory(individualBooking__user=user, stock__offer=offer)
    IndividualBookingFactory(individualBooking__user=user, stock__offer=offer)
    IndividualBookingFactory(individualBooking__user=user, isCancelled=True)

    assert _get_bookings_categories_and_subcategories(_get_user_bookings(user)) == (["FILM"], ["SUPPORT_PHYSIQUE_FILM"])
