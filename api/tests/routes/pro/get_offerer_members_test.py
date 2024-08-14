import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import assert_num_queries
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

        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        # 1. user_session
        # 2. user
        # 3. SELECT EXISTS user
        # 4. offerer
        # 5. user_offerer
        # 6. offerer_invitation
        with assert_num_queries(6):
            response = client.get(f"/offerers/{offerer_id}/members")
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

        client = client.with_session_auth(email=pro_user.email)
        offerer_id = offerer.id
        # 1. user_session
        # 2. user
        # 3. user
        # 4. DELETE FROM user
        # 5. user
        # 6. INSERT INTO user_session
        # 7. user
        # 8. user_offerer
        # 9. user_pro_new_nav_state
        # 10. SELECT EXISTS user_offerer
        # 11. user_session
        # 12. user
        # 13. user_offerer
        with assert_num_queries(13):
            response = client.with_session_auth(email=pro_user.email).get(f"/offerers/{offerer_id}/members")
            assert response.status_code == 403
