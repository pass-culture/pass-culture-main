from unittest.mock import patch

from models import OfferSQLEntity, Product
from repository import repository
from scripts.deactivate_inappropriate_offers import deactivate_inappropriate_offers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_product_with_thing_type


class DeactivateInappropriateOffersTest:
    @patch('scripts.deactivate_inappropriate_offers.redis')
    @clean_database
    def test_should_deactivate_offers_with_inappropriate_content(self, mocked_redis, app):
        # Given
        offerer = create_offerer()
        product_1 = create_product_with_thing_type(description='premier produit inapproprié')
        product_2 = create_product_with_thing_type(description='second produit inapproprié')
        venue = create_venue(offerer)
        offer_1 = create_offer_with_thing_product(product=product_1, venue=venue)
        offer_2 = create_offer_with_thing_product(product=product_2, venue=venue)
        repository.save(offer_1, offer_2)

        # When
        deactivate_inappropriate_offers([offer_1.id, offer_2.id])

        # Then
        products = Product.query.all()
        offers = OfferSQLEntity.query.all()
        first_product = products[0]
        second_product = products[1]
        first_offer = offers[0]
        second_offer = offers[1]

        assert not first_product.isGcuCompatible
        assert not second_product.isGcuCompatible
        assert not first_offer.isActive
        assert not second_offer.isActive
        for o in offers:
            mocked_redis.add_offer_id.assert_any_call(client=app.redis_client, offer_id=o.id)
