import pytest

import pcapi.core.educational.factories as collective_factories
from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    @pytest.mark.parametrize(
        "adage_id,collective_ds_application,is_onboarded",
        [
            (None, None, False),
            ("1", None, True),
            (None, "1", True),
            ("1", "1", True),
        ],
    )
    def test_get_offerer_eligibility_success(self, client, adage_id, collective_ds_application, is_onboarded):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, adageId=adage_id)
        if collective_ds_application is not None:
            collective_factories.CollectiveDmsApplicationFactory(venue=venue, procedure=collective_ds_application)

        offerer_id = offerer.id
        client = client.with_session_auth(pro.email)
        response = client.get(f"/offerers/{offerer_id}/eligibility")
        assert response.status_code == 200
        assert response.json.get("isOnboarded") is is_onboarded
        assert adage_id is None or response.json.get("hasAdageId")
        if adage_id is None:
            assert collective_ds_application is None or response.json.get("hasDsApplication")


class Return400Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer
    num_queries += 1  # rollback (atomic)

    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(email=pro.email)
        offerer_id = 0
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/eligibility")
            assert response.status_code == 403
