from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.users.external.batch import BATCH_DATETIME_FORMAT
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import UserRole
import pcapi.notifications.push.testing as push_testing
from pcapi.scripts.external_users.batch_update_users_attributes import format_batch_users
from pcapi.scripts.external_users.batch_update_users_attributes import format_sendinblue_users
from pcapi.scripts.external_users.batch_update_users_attributes import get_users_chunks
from pcapi.scripts.external_users.batch_update_users_attributes import run


@pytest.mark.usefixtures("db_session")
def test_get_users_chunks():
    """
    Test that the correct number of chunks have been fetched, that each one
    does not exceed the maximum chunk size, and that all of the users have been
    fetched.
    """
    users = UserFactory.create_batch(15)
    chunks = list(get_users_chunks(6))

    assert len(chunks) == 3
    assert [len(chunk) for chunk in chunks] == [6, 6, 3]

    expected_ids = {user.id for user in users}
    found_ids = {user.id for chunk in chunks for user in chunk}
    assert found_ids == expected_ids


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
def test_run(mock_import_contacts):
    """
    Test that two chunks of users are used and therefore two requests are sent.
    """
    UserFactory.create_batch(5)
    run(4)

    assert len(push_testing.requests) == 2
    assert len(mock_import_contacts.call_args_list) == 2


@pytest.mark.usefixtures("db_session")
def test_run_batch_only():
    """
    Test that two chunks of users are used and therefore two requests are sent.
    """
    UserFactory.create_batch(5)
    run(4, synchronize_sendinblue=False)

    assert len(push_testing.requests) == 2


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
def test_run_sendinblue_only(mock_import_contacts):
    """
    Test that two chunks of users are used and therefore two requests are sent.
    """
    UserFactory.create_batch(5)
    run(4, synchronize_batch=False)

    assert len(mock_import_contacts.call_args_list) == 2


@pytest.mark.usefixtures("db_session")
def test_format_batch_user():
    user = BeneficiaryGrant18Factory(deposit__version=1, departementCode="75")
    booking = IndividualBookingFactory(individualBooking__user=user)

    res = format_batch_users([user])

    assert len(res) == 1
    assert res[0].attributes == {
        "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "date(u.date_of_birth)": user.dateOfBirth.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_expiration_date)": user.deposit_expiration_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.last_booking_date)": booking.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.credit": 49000,
        "u.departement_code": "75",
        "u.is_beneficiary": True,
        "u.first_name": "Jeanne",
        "u.has_completed_id_check": True,
        "u.last_name": "Doux",
        "u.marketing_push_subscription": True,
        "u.postal_code": None,
        "ut.booking_categories": ["FILM"],
        "ut.roles": [UserRole.BENEFICIARY.value],
    }


@pytest.mark.usefixtures("db_session")
def test_format_sendinblue_user():
    user = BeneficiaryGrant18Factory(deposit__version=1, departementCode="75")
    booking = IndividualBookingFactory(individualBooking__user=user)

    res = format_sendinblue_users([user])

    assert len(res) == 1
    assert res[0].email == user.email
    assert res[0].attributes == {
        "BOOKED_OFFER_CATEGORIES": "FILM",
        "BOOKED_OFFER_SUBCATEGORIES": "SUPPORT_PHYSIQUE_FILM",
        "BOOKING_COUNT": 1,
        "CREDIT": Decimal("490.00"),
        "DATE_CREATED": user.dateCreated,
        "DATE_OF_BIRTH": user.dateOfBirth,
        "DEPARTMENT_CODE": "75",
        "DEPOSIT_ACTIVATION_DATE": user.deposit_activation_date,
        "DEPOSIT_EXPIRATION_DATE": user.deposit_expiration_date,
        "DMS_APPLICATION_APPROVED": None,
        "DMS_APPLICATION_SUBMITTED": None,
        "ELIGIBILITY": user.eligibility,
        "FIRSTNAME": "Jeanne",
        "HAS_BOOKINGS": None,
        "HAS_COMPLETED_ID_CHECK": True,
        "HAS_OFFERS": None,
        "INITIAL_CREDIT": Decimal("500.00"),
        "IS_BENEFICIARY": True,
        "IS_BENEFICIARY_18": True,
        "IS_BOOKING_EMAIL": None,
        "IS_ELIGIBLE": user.is_eligible,
        "IS_EMAIL_VALIDATED": user.isEmailValidated,
        "IS_PERMANENT": None,
        "IS_PRO": False,
        "IS_UNDERAGE_BENEFICIARY": False,
        "IS_USER_EMAIL": None,
        "IS_VIRTUAL": None,
        "LASTNAME": "Doux",
        "LAST_BOOKING_DATE": booking.dateCreated,
        "LAST_FAVORITE_CREATION_DATE": None,
        "LAST_VISIT_DATE": None,
        "MARKETING_EMAIL_SUBSCRIPTION": True,
        "OFFERER_NAME": None,
        "POSTAL_CODE": None,
        "PRODUCT_BRUT_X_USE_DATE": None,
        "USER_ID": user.id,
        "USER_IS_ATTACHED": None,
        "USER_IS_CREATOR": None,
        "VENUE_COUNT": None,
        "VENUE_LABEL": None,
        "VENUE_NAME": None,
        "VENUE_TYPE": None,
    }
