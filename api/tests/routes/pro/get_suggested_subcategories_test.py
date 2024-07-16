from datetime import datetime
from datetime import timedelta
from unittest import mock

import pytest
import time_machine

from pcapi.core import testing
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.connectors.suggestion import fixtures


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_access_by_no_one(self, client):
        response = client.get("/offers/suggested-subcategories?offer_name=foo")

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, client):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        # When
        response = client.with_session_auth(email=beneficiary.email).get("/jambon?offer_name=foo")

        # Then
        # breakpoint()
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__offererAddress=None
        )

        # When
        response = client.with_session_auth(email=pro_user.email).get(f"/jambon?offer_name=foo")

        # Then
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
class Returns200Test:
    #     # session
    #     # user
    #     # venue
    num_queries = 3

    def test_suggest_subcategories(self, mock_get_id_token_from_google, requests_mock, client):
        # Given
        pro = users_factories.ProFactory()
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/categorisation",
            json=fixtures.SUGGESTION_MUSEE_RESULT,
        )

        # When
        with testing.assert_num_queries(self.num_queries):
            response = client.with_session_auth(email=pro.email).get("/offers/suggested-subcategories?offer_name=foo")

        # Then
        assert response.status_code == 200
        assert response.json == {"subcategoryIds": ["VISITE_GUIDEE", "VISITE", "EVENEMENT_PATRIMOINE"]}
