from datetime import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.external import update_external_user
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.notifications.push import testing as batch_testing


MAX_BATCH_PARAMETER_SIZE = 30

pytestmark = pytest.mark.usefixtures("db_session")


def test_update_external_user():
    user = BeneficiaryFactory(dateOfBirth=datetime(2000, 1, 1))
    BookingFactory(user=user)

    n_query_get_user = 1
    n_query_get_bookings = 1
    n_query_get_deposit = 1

    with assert_num_queries(n_query_get_user + n_query_get_bookings + n_query_get_deposit):
        update_external_user(user)

    assert len(batch_testing.requests) == 1
    assert len(sendinblue_testing.sendinblue_requests) == 1
