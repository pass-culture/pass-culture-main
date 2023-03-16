from typing import Any

import pytest

from pcapi import settings
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class ProUpdateEmailTest:
    origin_email = "email@example.com"
    new_email = "updated_" + origin_email

    def test_beneficiary_updates_pro_email_(self, client: Any) -> None:
        user = users_factories.BeneficiaryGrant18Factory(email=self.origin_email)
        form_data = {"email": self.new_email, "password": settings.TEST_DEFAULT_PASSWORD}
        client = client.with_session_auth(user.email)
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 400
        assert user.email == self.origin_email

    def test_update_pro_email(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        form_data = {"email": self.new_email, "password": settings.TEST_DEFAULT_PASSWORD}
        client = client.with_session_auth(pro.email)
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 400
        assert response.json == {"email": ["Désactivation temporaire"]}
