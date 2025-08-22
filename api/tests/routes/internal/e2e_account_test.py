import pytest

from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class AccountCreationTest:
    def test_generate_beneficiary(self, client):
        response = client.post(
            "/native/v1/account/e2e",
            json={
                "age": 18,
                "idProvider": "ubble",
                "step": "beneficiary",
                "dateCreated": "2025-01-01T01:23:45",
                "transition1718": False,
                "postalCode": "91000",
            },
        )
        assert response.status_code == 200, response.json

        user = users_models.User.query.one()
        assert user.is_beneficiary
        assert response.json.get("confirmationLink") is not None
