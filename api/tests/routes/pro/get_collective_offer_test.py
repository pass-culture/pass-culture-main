import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_access_by_beneficiary(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
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
        assert "institution" in response.json
        assert response.json["isVisibilityEditable"] == True
        assert response_json["nonHumanizedId"] == offer.id

    def test_performance(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        humanized_offer_id = humanize(offer.id)

        num_queries = 2

        with testing.assert_num_queries(num_queries):
            client.get(f"/collective//offers/{humanized_offer_id}")


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email=pro_user.email)
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 403
