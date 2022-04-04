import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_access_by_beneficiary(self, client):
        # Given
        beneficiary = users_factories.ProFactory()
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)

        # When
        client = client.with_session_auth(email=beneficiary.email)
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationToken" not in response_json["venue"]["managingOfferer"]
        assert "dateCreated" in response_json
        assert response_json["nonHumanizedId"] == offer.id

    def test_performance(self, client):
        # Given
        beneficiary = users_factories.ProFactory()
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)

        # When
        client.with_session_auth(email=beneficiary.email)
        humanized_offer_id = humanize(offer.id)

        num_queries = 2

        with testing.assert_num_queries(num_queries):
            client.get(f"/collective//offers/{humanized_offer_id}")
