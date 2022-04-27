import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_user_offerer_should_return_only_user_offerer_from_current_user(self, client):
        # given
        user1 = users_factories.ProFactory(email="patrick.fiori@example.com")
        user2 = users_factories.ProFactory(email="celine.dion@example.com")
        offerer = offerers_factories.OffererFactory(siren="123456781")
        user_offerer1 = offerers_factories.UserOffererFactory(user=user1, offerer=offerer)
        user_offerer2 = offerers_factories.UserOffererFactory(user=user2, offerer=offerer)
        repository.save(user_offerer1, user_offerer2)

        # when
        response = client.with_session_auth(email=user1.email).get("/userOfferers/" + humanize(offerer.id))

        # then
        assert response.status_code == 200
        user_offerer_response = response.json[0]
        assert user_offerer_response["userId"] == humanize(user1.id)
        assert "validationToken" not in user_offerer_response

    @pytest.mark.usefixtures("db_session")
    def when_offerer_id_does_not_exist(self, client):
        # given
        user1 = users_factories.ProFactory(email="patrick.fiori@example.com")
        user2 = users_factories.ProFactory(email="celine.dion@example.com")
        offerer = offerers_factories.OffererFactory(siren="123456781")
        user_offerer1 = offerers_factories.UserOffererFactory(user=user1, offerer=offerer)
        user_offerer2 = offerers_factories.UserOffererFactory(user=user2, offerer=offerer)
        repository.save(user_offerer1, user_offerer2)
        non_existing_offerer_id = "B9"

        # when
        response = client.with_session_auth(email=user1.email).get("/userOfferers/" + non_existing_offerer_id)

        # then
        assert response.status_code == 200
        assert response.json == []
