from typing import Any

import pytest

import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_educational_partners(self, client: Any) -> None:
        # Given
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/cultural-partners")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "partners": [
                {
                    "id": 0,
                    "libelle": "string",
                    "communeLibelle": "string",
                    "regionLibelle": "string",
                },
                {
                    "id": 1,
                    "libelle": "string",
                    "communeLibelle": "string",
                    "regionLibelle": "string",
                },
            ]
        }


class Return401Test:
    def test_get_educational_partners_no_user_login(self, client: Any) -> None:
        # Given

        response = client.get("/cultural-partners")

        # Then
        assert response.status_code == 401
