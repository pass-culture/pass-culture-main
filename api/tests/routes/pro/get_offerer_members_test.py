import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
from pcapi.models.validation_status_mixin import ValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_offerer_members_by_pro(self, client):
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
        offerers_factories.OffererInvitationFactory(
            email="member.pro@example.com", user=pro, offerer=offerer, status=offerers_models.InvitationStatus.ACCEPTED
        )

        response = client.with_session_auth(email=pro.email).get(f"/offerers/{offerer.id}/members")

        assert response.status_code == 200
        assert response.json["members"] == [
            {"email": "invited.pro@example.com", "status": "pending"},
            {"email": "pending.pro@example.com", "status": "pending"},
            {"email": "member.pro@example.com", "status": "validated"},
            {"email": "offerer@example.com", "status": "validated"},
        ]


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

        response = client.with_session_auth(email=pro_user.email).get(f"/offerers/{offerer.id}/members")

        assert response.status_code == 403
