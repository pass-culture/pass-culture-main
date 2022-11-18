from flask import g
from flask import url_for
import pytest

import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.routes.backoffice_v3.filters import format_date

from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


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


class GetProUserHistoryTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.pro_user.get_user_history"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_history(self, authenticated_client, pro_user):
        action = history_factories.ActionHistoryFactory(user=pro_user)
        url = url_for("backoffice_v3_web.pro_user.get_user_history", user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert action.comment in content
        assert action.authorUser.full_name in content
        assert format_date(action.actionDate, "Le %d/%m/%Y à %Hh%M") in content

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_no_history(self, authenticated_client, pro_user):
        url = url_for("backoffice_v3_web.pro_user.get_user_history", user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200


class CommentProUserTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf, unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.pro_user.comment_pro_user"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_add_comment(self, client, legit_user, pro_user):
        comment = "J'aime les commentaires en français !"
        response = self.send_comment_pro_user_request(client, legit_user, pro_user, comment)

        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.pro_user.get", user_id=pro_user.id, _external=True)
        assert response.location == expected_url

        assert len(pro_user.action_history) == 1
        assert pro_user.action_history[0].user == pro_user
        assert pro_user.action_history[0].authorUser == legit_user
        assert pro_user.action_history[0].comment == comment

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_add_invalid_comment(self, client, legit_user, pro_user):
        response = self.send_comment_pro_user_request(client, legit_user, pro_user, "")

        assert response.status_code == 302
        assert not pro_user.action_history

    def send_comment_pro_user_request(self, client, legit_user, pro_user, comment):
        authenticated_client = client.with_bo_session_auth(legit_user)

        # generate and fetch (inside g) csrf token
        pro_user_detail_url = url_for("backoffice_v3_web.pro_user.get", user_id=pro_user.id)
        authenticated_client.get(pro_user_detail_url)

        url = url_for("backoffice_v3_web.pro_user.comment_pro_user", user_id=pro_user.id)
        form = {"comment": comment, "csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)
