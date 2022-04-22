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
        offer = educational_factories.CollectiveOfferTemplateFactory()

        # When
        client = client.with_session_auth(email=beneficiary.email)
        response = client.get(f"/collective/offers-template/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationToken" not in response_json["venue"]["managingOfferer"]
        assert "stock" not in response_json
        assert "dateCreated" in response_json
        assert "educationalPriceDetail" in response_json
        assert response_json["name"] == offer.name
        assert response_json["nonHumanizedId"] == offer.id
        assert response_json["venue"]["id"] == humanize(offer.venue.id)
        assert response_json["venueId"] == humanize(offer.venue.id)

    def test_performance(self, client):
        # Given
        beneficiary = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory()

        # When
        client.with_session_auth(email=beneficiary.email)
        humanized_offer_id = humanize(offer.id)

        num_queries = 1  # select collective offer template

        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES + num_queries):
            client.get(f"/collective/offers-template/{humanized_offer_id}")
