from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.testing import assert_num_queries

from tests.routes.pro.utils import collective_offers as test_utils


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory()


@pytest.fixture(name="offer")
def offer_fixture(redactor):
    offer = educational_factories.CollectiveStockFactory().collectiveOffer
    educational_factories.CollectiveOfferEducationalRedactorFactory(
        collectiveOfferId=offer.id, educationalRedactorId=redactor.id
    )
    return offer


@pytest.fixture(name="offer_template")
def offer_template_fixture(redactor):
    offer_template = educational_factories.CollectiveOfferTemplateFactory()
    educational_factories.CollectiveOfferTemplateEducationalRedactorFactory(
        collectiveOfferTemplateId=offer_template.id, educationalRedactorId=redactor.id
    )
    return offer_template


@pytest.fixture(name="test_client")
def test_client_fixture(client, redactor):
    return client.with_adage_token(email=redactor.email)


class GetFavoriteOfferTest:
    endpoint = "adage_iframe.get_collective_favorites"

    def test_get_favorites(self, test_client, offer, offer_template):
        with assert_num_queries(3):
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200

        expected_offer = test_utils.expected_collective_offer_serialization(offer)
        expected_template = test_utils.expected_collective_offer_template_serialization(offer_template)

        assert response.json == {
            "favoritesOffer": [expected_offer],
            "favoritesTemplate": [expected_template],
        }

    def test_get_favorite_offer_only(self, test_client, offer):
        with assert_num_queries(3):
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json["favoritesOffer"]
        assert not response.json["favoritesTemplate"]

    def test_get_favorite_template_only_test(self, test_client, offer_template):
        with assert_num_queries(3):
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert not response.json["favoritesOffer"]
        assert response.json["favoritesTemplate"]
