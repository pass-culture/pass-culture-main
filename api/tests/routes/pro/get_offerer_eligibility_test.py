import random
import pytest

from pcapi.core import testing
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return400Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer
    num_queries += 1  # rollback (atomic)

    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(email=pro.email)
        offerer_id = random.randint(1, 100)
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/eligibility")
            assert response.status_code == 403
