import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_user_offerer_should_return_only_user_offerer_from_current_user(self, app):
        # given
        user1 = users_factories.UserFactory(email="patrick.fiori@test.com")
        user2 = users_factories.UserFactory(email="celine.dion@test.com")
        offerer = create_offerer(siren="123456781")
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        repository.save(user_offerer1, user_offerer2)

        # when
        response = (
            TestClient(app.test_client()).with_auth(email=user1.email).get("/userOfferers/" + humanize(offerer.id))
        )

        # then
        assert response.status_code == 200
        user_offerer_response = response.json[0]
        assert user_offerer_response["userId"] == humanize(user1.id)
        assert "validationToken" not in user_offerer_response

    @pytest.mark.usefixtures("db_session")
    def when_offerer_id_does_not_exist(self, app):
        # given
        user1 = users_factories.UserFactory(email="patrick.fiori@test.com")
        user2 = users_factories.UserFactory(email="celine.dion@test.com")
        offerer = create_offerer(siren="123456781")
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        repository.save(user_offerer1, user_offerer2)
        non_existing_offerer_id = "B9"

        # when
        response = (
            TestClient(app.test_client()).with_auth(email=user1.email).get("/userOfferers/" + non_existing_offerer_id)
        )

        # then
        assert response.status_code == 200
        assert response.json == []
