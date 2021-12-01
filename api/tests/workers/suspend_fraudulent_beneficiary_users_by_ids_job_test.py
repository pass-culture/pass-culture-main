from unittest import mock

import pytest

from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.workers.suspend_fraudulent_beneficiary_users_by_ids_job import (
    suspend_fraudulent_beneficiary_users_by_ids_job,
)


@mock.patch("pcapi.workers.suspend_fraudulent_beneficiary_users_by_ids_job.send_suspended_fraudulent_users_email")
@mock.patch("pcapi.workers.suspend_fraudulent_beneficiary_users_by_ids_job.suspend_fraudulent_beneficiary_users_by_ids")
@pytest.mark.usefixtures("db_session")
def test_send_email_is_called(
    mocked_suspend_fraudulent_benef_users_by_ids, mocked_send_suspended_fraudulent_users_email
) -> None:
    admin_user = AdminFactory(email="admin@example.com")
    fraudulent_user = BeneficiaryGrant18Factory(id=15)
    mocked_suspend_fraudulent_benef_users_by_ids.return_value = {
        "fraudulent_users": [fraudulent_user],
        "nb_cancelled_bookings": 0,
    }

    suspend_fraudulent_beneficiary_users_by_ids_job([15], admin_user)

    mocked_send_suspended_fraudulent_users_email.assert_called_once_with([fraudulent_user], 0, admin_user.email)
