import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.users.external.batch import BATCH_DATETIME_FORMAT
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import UserFactory
import pcapi.notifications.push.testing as push_testing
from pcapi.scripts.batch_update_users_attributes import format_users
from pcapi.scripts.batch_update_users_attributes import get_users_chunks
from pcapi.scripts.batch_update_users_attributes import run


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
def test_run():
    """
    Test that two chunks of users are used and therefore two requests are sent.
    """
    UserFactory.create_batch(5)
    run(4)

    assert len(push_testing.requests) == 2


@pytest.mark.usefixtures("db_session")
def test_format_user():
    user = BeneficiaryFactory()
    booking = BookingFactory(user=user)

    res = format_users([user])

    assert len(res) == 1
    assert res[0].attributes == {
        "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "date(u.date_of_birth)": user.dateOfBirth.strftime(BATCH_DATETIME_FORMAT),
        "date(u.deposit_expiration_date)": user.deposit_expiration_date.strftime(BATCH_DATETIME_FORMAT),
        "date(u.last_booking_date)": booking.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.credit": 49000,
        "u.departement_code": "75",
        "u.is_beneficiary": True,
        "u.marketing_push_subscription": True,
        "u.postal_code": None,
        "ut.booking_categories": ["FILM"],
    }
