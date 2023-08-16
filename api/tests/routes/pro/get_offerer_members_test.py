import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models.validation_status_mixin import ValidationStatus

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @override_features(WIP_ENABLE_NEW_USER_OFFERER_LINK=True)
    def test_get_offerer_members_by_pro(self, app):
        pro = users_factories.ProFactory(email="offerer@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="member.pro@example.com")
        offerers_factories.NotValidatedUserOffererFactory(
            offerer=offerer, validationStatus=ValidationStatus.PENDING, user__email="pending.pro@example.com"
        )
        offerers_factories.NotValidatedUserOffererFactory(
            offerer=offerer, validationStatus=ValidationStatus.REJECTED, user__email="rejected.pro@example.com"
        )
        offerers_factories.OffererInvitationFactory(email="invited.pro@example.com", user=pro, offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth(email=pro.email)
        response = client.get(f"/offerers/{offerer.id}/members")

        assert response.status_code == 200
        assert sorted(response.json["members"], key=lambda member: member["email"]) == [
            {"email": "invited.pro@example.com", "status": "pending"},
            {"email": "member.pro@example.com", "status": "validated"},
            {"email": "offerer@example.com", "status": "validated"},
            {"email": "pending.pro@example.com", "status": "pending"},
        ]


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @override_features(WIP_ENABLE_NEW_USER_OFFERER_LINK=True)
    def test_access_by_unauthorized_pro_user(self, app):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

        client = TestClient(app.test_client()).with_session_auth(email=pro_user.email)
        response = client.get(f"/offerers/{offerer.id}/members")

        assert response.status_code == 403
