from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories

from .helpers import unauthorized as unauthorized_helpers


pytestmark = pytest.mark.usefixtures("db_session")


class GetProUserTest:
    endpoint = "backoffice_v3_web.pro_user.get"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.pro_user.get"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_pro_user(self, authenticated_client):  # type: ignore
        user = offerers_factories.UserOffererFactory(user__phoneNumber="+33638656565", user__postalCode="29000").user
        url = url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert str(user.id) in content
        assert user.firstName in content
        assert user.lastName.upper() in content
        assert user.email in content
        assert user.phoneNumber in content
        assert user.postalCode in content
        assert user.departementCode in content
        assert "Pro" in content

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_not_pro_user(self, authenticated_client):  # type: ignore
        user = users_factories.BeneficiaryGrant18Factory()
        url = url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.search_pro", _external=True)
        assert response.location == expected_url
