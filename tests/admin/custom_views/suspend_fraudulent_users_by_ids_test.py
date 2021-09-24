import io

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import UsedBookingFactory
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory


@pytest.mark.usefixtures("db_session")
class SuspendFraudulentUsersByIdsTest:
    def test_suspend_users_by_ids(self, client):
        admin_user = AdminFactory()
        fraudulent_user_1 = BeneficiaryGrant18Factory(id=5)
        fraudulent_user_2 = BeneficiaryGrant18Factory(id=16)
        BookingFactory(user=fraudulent_user_1)
        UsedBookingFactory(user=fraudulent_user_2)
        user_ids_csv = (io.BytesIO(b"user_id\n5\n16"), "user_ids.csv")
        files = {"user_ids_csv": user_ids_csv}
        headers = {"content-type": "multipart/form-data"}

        client = client.with_session_auth(admin_user.email)
        response = client.post("/pc/back-office/suspend_fraud_users_by_user_ids", files=files, headers=headers)

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert not fraudulent_user_2.isActive
        assert not fraudulent_user_1.isActive
        assert "Nombre d'utilisateurs suspendus : 2" in content
        assert "Nombre de réservations annulées : 1" in content
