import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_post_invite_member_again(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(user=pro_user, offerer=offerer, email="new.user@example.com")

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(
            f"/offerers/{offerer.id}/invite-again", json=data
        )

        assert response.status_code == 204
        assert db.session.query(offerers_models.OffererInvitation).one()


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_invitation_does_not_already_exist(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(
            f"/offerers/{offerer.id}/invite-again", json=data
        )

        assert response.status_code == 400
        assert response.json == {"email": "Impossible de renvoyer une invitation pour ce collaborateur"}

    def test_invitation_is_validated(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(
            user=pro_user,
            offerer=offerer,
            email="new.user@example.com",
            status=offerers_models.InvitationStatus.ACCEPTED,
        )

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(
            f"/offerers/{offerer.id}/invite-again", json=data
        )

        assert response.status_code == 400
        assert response.json == {"email": "Impossible de renvoyer une invitation pour ce collaborateur"}

    def test_user_offerer_already_exists(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        pro_user2 = users_factories.ProFactory(email="pro.user2@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.UserOffererFactory(user=pro_user2, offerer=offerer)

        data = {"email": "pro.user2@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(
            f"/offerers/{offerer.id}/invite-again", json=data
        )

        assert response.status_code == 400
        assert response.json == {"email": "Impossible de renvoyer une invitation pour ce collaborateur"}

    def test_user_has_not_access_to_offerer(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory(id=1)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(user=pro_user, offerer=offerer, email="new.user@example.com")

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post("/offerers/2/invite", json=data)

        assert response.status_code == 403
