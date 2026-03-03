import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns200ForProUserTest:
    def test_response_serializer(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_non_attached = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.PendingUserOffererFactory(user=pro_user, offerer=offerer_non_attached)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select validated offerers
        num_queries += 1  # select pending offerers
        with testing.assert_num_queries(num_queries):
            response = client.get("/offerers/names")
            assert response.status_code == 200

        assert response.json == {
            "offerersNames": [{"name": offerer.name, "id": offerer.id}],
            "offerersNamesWithPendingValidation": [{"name": offerer_non_attached.name, "id": offerer_non_attached.id}],
        }
