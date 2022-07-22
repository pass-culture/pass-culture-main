from typing import Any

import pytest
import requests_mock

from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_educational_partner(self, client: Any) -> None:
        # Given
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        response = client.get("/cultural-partner/33333333333333")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": 128028,
            "statutId": 3,
            "siteWeb": "http://www.fetedulivrejeunesse.fr/",
            "domaineIds": [1, 11],
        }


class Return401Test:
    def test_get_educational_partners_no_user_login(self, client: Any) -> None:
        # Given

        response = client.get("/cultural-partner/33333333333333")

        # Then
        assert response.status_code == 401


class Return404Test:
    @override_settings(
        ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
        ADAGE_API_URL="https://fake-url",
        ADAGE_API_KEY="fake-token",
    )
    def test_get_educational_partner_not_found(self, client: Any) -> None:
        # Given
        pro_user = users_factories.ProFactory()
        siret = "33333333333333"

        client.with_session_auth(pro_user.email)

        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://fake-url/v1/etablissement-culturel/{siret}",
                status_code=404,
                headers={"content-type": "application/json"},
                request_headers={
                    "X-omogen-api-key": "fake-token",
                },
            )
            response = client.get(f"/cultural-partner/{siret}")

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "CULTURAL_PARTNER_NOT_FOUND"}
