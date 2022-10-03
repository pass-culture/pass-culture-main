from unittest.mock import patch

import jwt
import pytest

from pcapi import settings
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @patch("pcapi.settings.METABASE_SITE_URL", "fakeUrl")
    @patch("pcapi.settings.METABASE_SECRET_KEY", "fakeKey")
    def test_user_with_access_to_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/offerers/{humanize(offerer.id)}/stats")
        dashboardUrl = response.json["dashboardUrl"].split("/")
        encodedToken = dashboardUrl[3].split("#")[0]
        payload = jwt.decode(encodedToken, settings.METABASE_SECRET_KEY, algorithms="HS256")

        assert response.status_code == 200
        assert dashboardUrl[0] == "fakeUrl"
        assert payload["resource"] == {"dashboard": 438}
        assert payload["params"] == {"siren": [offerer.siren]}


class Returns403Test:
    @patch("pcapi.settings.METABASE_SITE_URL", "fakeUrl")
    @patch("pcapi.settings.METABASE_SECRET_KEY", "fakeKey")
    def test_user_with_no_access_to_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = offerers_factories.OffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/offerers/{humanize(offerer.id)}/stats")

        assert response.status_code == 403
