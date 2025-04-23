import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_post_invite_member(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(f"/offerers/{offerer.id}/invite", json=data)

        assert response.status_code == 204
        offerer_invitation = db.session.query(offerers_models.OffererInvitation).one()
        assert offerer_invitation.email == "new.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_invitation_already_exists(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(user=pro_user, offerer=offerer, email="new.user@example.com")

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post(f"/offerers/{offerer.id}/invite", json=data)

        assert response.status_code == 400
        assert response.json == {"email": "Une invitation a déjà été envoyée à ce collaborateur"}

    def test_user_has_not_access_to_offerer(self, client):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory(id=1)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        data = {"email": "new.user@example.com"}

        response = client.with_session_auth("pro.user@example.com").post("/offerers/2/invite", json=data)

        assert response.status_code == 403
