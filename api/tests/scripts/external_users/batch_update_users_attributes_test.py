import datetime
from decimal import Decimal
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.external.batch import BATCH_DATETIME_FORMAT
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import FavoriteFactory
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
@patch("pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
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
@patch("pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
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
        "date(u.date_of_birth)": user.dateOfBirth.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_activation_date)": user.deposit_activation_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_expiration_date)": user.deposit_expiration_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.last_booking_date)": booking.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.booked_offer_categories_count": 1,
        "u.booking_count": 1,
        "u.booking_venues_count": 1,
        "u.city": "Paris",
        "u.credit": 28990,
        "u.departement_code": "75",
        "u.deposits_count": 1,
        "u.is_beneficiary": True,
        "u.is_current_beneficiary": True,
        "u.is_former_beneficiary": False,
        "u.first_name": "Jeanne",
        "u.has_completed_id_check": True,
        "u.last_name": "Doux",
        "u.marketing_push_subscription": True,
        "u.most_booked_movie_genre": None,
        "u.most_booked_music_type": None,
        "u.most_booked_subcategory": "SUPPORT_PHYSIQUE_FILM",
        "ut.most_favorite_offer_subcat": ["SUPPORT_PHYSIQUE_FILM"],
        "u.postal_code": None,
        "ut.booking_categories": ["FILM"],
        "ut.booking_subcategories": ["SUPPORT_PHYSIQUE_FILM"],
        "ut.roles": [UserRole.BENEFICIARY.value],
    }


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-12-06 10:00:00")  # Keep time frozen in 2022 as long as we send *_2022 attributes
def test_format_sendinblue_user():
    user = BeneficiaryGrant18Factory(departementCode="75")
    booking = BookingFactory(user=user, dateCreated=datetime.datetime(2022, 12, 6, 10))
    favorite = FavoriteFactory(user=user)

    res = format_sendinblue_users([user])

    assert len(res) == 1
    assert res[0].email == user.email
    assert res[0].attributes == {
        "BOOKED_OFFER_CATEGORIES": "FILM",
        "BOOKED_OFFER_CATEGORIES_COUNT": 1,
        "BOOKED_OFFER_SUBCATEGORIES": "SUPPORT_PHYSIQUE_FILM",
        "BOOKING_COUNT": 1,
        "BOOKING_VENUES_COUNT": 1,
        "CREDIT": Decimal("289.90"),
        "DATE_CREATED": user.dateCreated,
        "DATE_OF_BIRTH": user.dateOfBirth,
        "DEPARTMENT_CODE": "75",
        "DEPOSITS_COUNT": 1,
        "DEPOSIT_ACTIVATION_DATE": user.deposit_activation_date,
        "DEPOSIT_EXPIRATION_DATE": user.deposit_expiration_date,
        "DMS_APPLICATION_APPROVED": None,
        "DMS_APPLICATION_SUBMITTED": None,
        "ELIGIBILITY": user.eligibility,
        "FIRSTNAME": "Jeanne",
        "HAS_BOOKINGS": None,
        "HAS_COMPLETED_ID_CHECK": True,
        "HAS_OFFERS": None,
        "INITIAL_CREDIT": Decimal("300.00"),
        "IS_BENEFICIARY": True,
        "IS_BENEFICIARY_18": True,
        "IS_BOOKING_EMAIL": None,
        "IS_CURRENT_BENEFICIARY": True,
        "IS_EAC": None,
        "IS_FORMER_BENEFICIARY": False,
        "IS_ELIGIBLE": user.is_eligible,
        "IS_EMAIL_VALIDATED": user.isEmailValidated,
        "IS_PERMANENT": None,
        "IS_PRO": False,
        "IS_TAGGED_COLLECTIVITE": None,
        "IS_UNDERAGE_BENEFICIARY": False,
        "IS_USER_EMAIL": None,
        "IS_VIRTUAL": None,
        "LASTNAME": "Doux",
        "LAST_BOOKING_DATE": booking.dateCreated,
        "LAST_FAVORITE_CREATION_DATE": favorite.dateCreated,
        "LAST_VISIT_DATE": user.lastConnectionDate,
        "MARKETING_EMAIL_SUBSCRIPTION": True,
        "MOST_BOOKED_OFFER_SUBCATEGORY": "SUPPORT_PHYSIQUE_FILM",
        "MOST_BOOKED_MOVIE_GENRE": None,
        "MOST_BOOKED_MUSIC_TYPE": None,
        "MOST_FAVORITE_OFFER_SUBCATEGORIES": "SUPPORT_PHYSIQUE_FILM",
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
        "AMOUNT_SPENT_2022": Decimal("10.10"),
        "FIRST_BOOKED_OFFER_2022": booking.stock.offer.name,
        "LAST_BOOKED_OFFER_2022": booking.stock.offer.name,
        "HAS_COLLECTIVE_OFFERS": None,
    }
