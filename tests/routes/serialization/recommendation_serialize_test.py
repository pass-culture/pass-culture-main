from routes.serialization.recommendation_serialize import serialize_recommendation, serialize_recommendations
from tests.test_utils import create_recommendation, create_user, create_offerer, create_venue, \
    create_mediation, create_stock, \
    create_offer_with_thing_product, create_product_with_thing_type


class SerializeRecommendationTest:
    def test_should_return_serialized_recommendation(self):
        # Given
        user = create_user(email='user@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(dominant_color=b'\x00\x00\x00', thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        recommendation = create_recommendation(offer, user, mediation=mediation)

        # When
        serialized_recommendation = serialize_recommendation(recommendation)

        # Then
        assert 'bookings' not in serialized_recommendation
        assert serialized_recommendation is not None


class SerializeRecommendationsTest:
    def test_should_return_serialized_recommendations(self):
        # Given
        user = create_user(email='user@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(dominant_color=b'\x00\x00\x00', thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        stock.offerId = 1
        mediation = create_mediation(offer)
        recommendation1 = create_recommendation(offer, user, mediation=mediation)
        recommendation2 = create_recommendation(offer, user, mediation=mediation)
        recommendation1.offerId = 1
        recommendation2.offerId = 2

        # When
        serialized_recommendations = serialize_recommendations([recommendation1, recommendation2])

        # Then
        assert len(serialized_recommendations) == 2
