from decimal import Decimal
from unittest.mock import patch

import pytest

import pcapi.notifications.push.testing as push_testing
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.external.batch import BATCH_DATETIME_FORMAT
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import FavoriteFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import UserRole
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
@patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
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
@patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
def test_run_sendinblue_only(mock_import_contacts):
    """
    Test that two chunks of users are used and therefore two requests are sent.
    """
    UserFactory.create_batch(5)
    run(4, synchronize_batch=False)

    assert len(mock_import_contacts.call_args_list) == 2


@pytest.mark.usefixtures("db_session")
def test_format_batch_user():
    user = BeneficiaryGrant18Factory(departementCode="75", city="Paris")
    booking = BookingFactory(user=user)
    FavoriteFactory(user=user)

    res = format_batch_users([user])

    assert len(res) == 1
    assert res[0].attributes == {
        "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "date(u.date_of_birth)": user.birth_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_activation_date)": user.deposit_activation_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_expiration_date)": user.deposit_expiration_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.last_booking_date)": booking.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.booked_offer_categories_count": 1,
        "u.booking_count": 1,
        "u.booking_venues_count": 1,
        "u.city": "Paris",
        "u.credit": 13990,
        "u.departement_code": "75",
        "u.deposits_count": 1,
        "u.is_beneficiary": True,
        "u.is_current_beneficiary": True,
        "u.is_former_beneficiary": False,
        "u.first_name": user.firstName,
        "u.has_completed_id_check": True,
        "u.last_name": user.lastName,
        "u.last_recredit_type": "Recredit18",
        "u.marketing_email_subscription": True,
        "u.marketing_push_subscription": True,
        "u.most_booked_movie_genre": None,
        "u.most_booked_music_type": None,
        "u.most_booked_subcategory": "SUPPORT_PHYSIQUE_FILM",
        "ut.most_favorite_offer_subcat": ["SUPPORT_PHYSIQUE_FILM"],
        "u.postal_code": None,
        "ut.permanent_theme_preference": None,
        "ut.booking_categories": ["FILM"],
        "ut.booking_subcategories": ["SUPPORT_PHYSIQUE_FILM"],
        "ut.roles": [UserRole.BENEFICIARY.value],
        "u.eligibility": EligibilityType.AGE17_18.value,
        "u.is_eligible": True,
    }


@pytest.mark.usefixtures("db_session")
def test_format_sendinblue_user():
    user = BeneficiaryGrant18Factory(departementCode="75")
    initial_credit = user.deposit.amount
    booking = BookingFactory(user=user)
    favorite = FavoriteFactory(user=user)
    credit_after_booking = initial_credit - booking.total_amount

    res = format_sendinblue_users([user])

    assert len(res) == 1
    assert res[0].email == user.email
    assert res[0].attributes == {
        "ACHIEVEMENTS": "",
        "BOOKED_OFFER_CATEGORIES": "FILM",
        "BOOKED_OFFER_CATEGORIES_COUNT": 1,
        "BOOKED_OFFER_SUBCATEGORIES": "SUPPORT_PHYSIQUE_FILM",
        "BOOKING_COUNT": 1,
        "BOOKING_VENUES_COUNT": 1,
        "CREDIT": Decimal(credit_after_booking),
        "DATE_CREATED": user.dateCreated,
        "DATE_OF_BIRTH": user.dateOfBirth,
        "DEPARTMENT_CODE": "75",
        "DEPOSITS_COUNT": 1,
        "DEPOSIT_ACTIVATION_DATE": user.deposit_activation_date,
        "DEPOSIT_EXPIRATION_DATE": user.deposit_expiration_date,
        "DMS_APPLICATION_APPROVED": None,
        "DMS_APPLICATION_SUBMITTED": None,
        "ELIGIBILITY": user.eligibility.value,
        "EAC_MEG": None,
        "FIRSTNAME": "Jeanne",
        "HAS_BANNER_URL": None,
        "HAS_BOOKINGS": None,
        "HAS_COLLECTIVE_OFFERS": None,
        "HAS_COMPLETED_ID_CHECK": True,
        "HAS_INDIVIDUAL_OFFERS": None,
        "HAS_OFFERS": None,
        "INITIAL_CREDIT": Decimal(initial_credit),
        "IS_ACTIVE_PRO": None,
        "IS_BENEFICIARY": True,
        "IS_BENEFICIARY_18": True,
        "IS_BOOKING_EMAIL": None,
        "IS_CURRENT_BENEFICIARY": True,
        "IS_EAC": None,
        "IS_FORMER_BENEFICIARY": False,
        "IS_ELIGIBLE": user.is_eligible,
        "IS_EMAIL_VALIDATED": user.isEmailValidated,
        "IS_OPEN_TO_PUBLIC": None,
        "IS_PERMANENT": None,
        "IS_PRO": False,
        "IS_UNDERAGE_BENEFICIARY": False,
        "IS_USER_EMAIL": None,
        "IS_VIRTUAL": None,
        "LASTNAME": "Doux",
        "LAST_BOOKING_DATE": booking.dateCreated,
        "LAST_FAVORITE_CREATION_DATE": favorite.dateCreated,
        "LAST_RECREDIT_TYPE": "Recredit18",
        "LAST_VISIT_DATE": user.lastConnectionDate,
        "MARKETING_EMAIL_SUBSCRIPTION": True,
        "MOST_BOOKED_OFFER_SUBCATEGORY": "SUPPORT_PHYSIQUE_FILM",
        "MOST_BOOKED_MOVIE_GENRE": None,
        "MOST_BOOKED_MUSIC_TYPE": None,
        "MOST_FAVORITE_OFFER_SUBCATEGORIES": "SUPPORT_PHYSIQUE_FILM",
        "OFFERER_NAME": None,
        "OFFERER_TAG": None,
        "PERMANENT_THEME_PREFERENCE": "",
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


@pytest.mark.usefixtures("db_session")
def test_format_sendinblue_pro():
    user_offerer = UserOffererFactory()
    user = user_offerer.user
    offerer = user_offerer.offerer
    venue = VenueFactory(bookingEmail=user.email, managingOfferer=offerer)

    res = format_sendinblue_users([user])

    assert len(res) == 1
    assert res[0].email == user.email
    assert res[0].attributes == {
        "FIRSTNAME": user.firstName,
        "IS_ACTIVE_PRO": True,
        "IS_PRO": True,
        "LASTNAME": user.lastName,
        "DMS_APPLICATION_SUBMITTED": False,
        "DMS_APPLICATION_APPROVED": False,
        "HAS_BANNER_URL": True,
        "HAS_BOOKINGS": False,
        "HAS_COLLECTIVE_OFFERS": False,
        "HAS_INDIVIDUAL_OFFERS": False,
        "HAS_OFFERS": False,
        "IS_EAC": False,
        "IS_EAC_MEG": False,
        "IS_BOOKING_EMAIL": True,
        "IS_OPEN_TO_PUBLIC": False,
        "IS_PERMANENT": False,
        "IS_USER_EMAIL": True,
        "IS_VIRTUAL": False,
        "MARKETING_EMAIL_SUBSCRIPTION": True,
        "OFFERER_NAME": offerer.name,
        "OFFERER_TAG": "",
        "USER_ID": user.id,
        "USER_IS_ATTACHED": False,
        "USER_IS_CREATOR": True,
        "VENUE_COUNT": 1,
        "VENUE_LABEL": "",
        "VENUE_NAME": venue.name,
        "VENUE_TYPE": venue.venueTypeCode.name,
    }
