import pytest

from pcapi.core import testing
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/finance/has-settlement"


class HasSettlementTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check if user_offerer exists
    num_queries += 1  # check if offerer has any settlement

    def test_with_settlement(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        factories.SettlementFactory(bankAccount__offerer=user_offerer.offerer, status=models.SettlementStatus.EXECUTED)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {"hasSettlement": True}

    def test_with_issued_settlement(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        factories.SettlementFactory(bankAccount__offerer=user_offerer.offerer, status=models.SettlementStatus.ISSUED)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {"hasSettlement": False}

    def test_with_no_settlement(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {"hasSettlement": False}

    def test_with_settlement_other_offerer(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        factories.SettlementFactory(status=models.SettlementStatus.EXECUTED)

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(URL, params={"offererId": offerer_id})

        assert response.status_code == 200
        assert response.json == {"hasSettlement": False}

    def test_no_access_to_offerer(self, client: TestClient):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        factories.SettlementFactory(bankAccount__offerer=offerer, status=models.SettlementStatus.EXECUTED)

        params = {"offererId": offerer.id}
        client = client.with_session_auth(user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # check if user_offerer exists
        num_queries += 1  # rollback
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params=params)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_no_offerer_id(self, client: TestClient):
        user = users_factories.ProFactory()

        client = client.with_session_auth(user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback
        with testing.assert_num_queries(num_queries):
            response = client.get(URL, params={})

        assert response.status_code == 400
        assert response.json == {"offererId": ["Ce champ est obligatoire"]}
