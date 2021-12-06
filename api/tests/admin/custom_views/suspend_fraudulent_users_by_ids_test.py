import io
from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory


@pytest.mark.usefixtures("db_session")
class SuspendFraudulentUsersByIdsTest:
    @patch(
        "pcapi.admin.custom_views.suspend_fraudulent_users_by_ids.suspend_fraudulent_beneficiary_users_by_ids_job.delay"
    )
    def test_suspend_users_by_ids(self, mocked_suspend_fraudulent_beneficiary_users_by_ids_job, client):
        admin_user = AdminFactory(email="admin@example.com")
        fraudulent_user_1 = BeneficiaryGrant18Factory(id=5)
        fraudulent_user_2 = BeneficiaryGrant18Factory(id=16)
        booking_factories.IndividualBookingFactory(individualBooking__user=fraudulent_user_1)
        booking_factories.UsedIndividualBookingFactory(individualBooking__user=fraudulent_user_2)
        user_ids_csv = (io.BytesIO(b"user_id\n5\n16"), "user_ids.csv")
        files = {"user_ids_csv": user_ids_csv}
        headers = {"content-type": "multipart/form-data"}

        client = client.with_session_auth(admin_user.email)
        response = client.post("/pc/back-office/suspend_fraud_users_by_user_ids", files=files, headers=headers)

        mocked_suspend_fraudulent_beneficiary_users_by_ids_job.assert_called_once_with([5, 16], admin_user)
        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "La suspension des utilisateurs via ids a bien été lancée" in content
