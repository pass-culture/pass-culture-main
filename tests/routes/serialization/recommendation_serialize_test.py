from unittest.mock import patch

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_recommendation
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.routes.serialization.recommendation_serialize import serialize_recommendation
from pcapi.routes.serialization.recommendation_serialize import serialize_recommendations


class SerializeRecommendationTest:
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def test_should_return_booking_if_query_booking_is_True(self, find_from_recommendation):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        recommendation = create_recommendation(offer, user, mediation=mediation)
        find_from_recommendation.return_value = [
            create_booking(user=user, stock=stock, venue=venue, recommendation=recommendation)
        ]

        # When
        serialized_recommendation = serialize_recommendation(recommendation, user, query_booking=True)

        # Then
        assert "bookings" in serialized_recommendation
        assert serialized_recommendation["bookings"] is not None

    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def test_should_not_return_booking_if_query_booking_is_False(self, find_from_recommendation):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        recommendation = create_recommendation(offer, user, mediation=mediation)
        find_from_recommendation.return_value = [
            create_booking(user=user, stock=stock, venue=venue, recommendation=recommendation)
        ]

        # When
        serialized_recommendation = serialize_recommendation(recommendation, user, query_booking=False)

        # Then
        assert "bookings" not in serialized_recommendation


class SerializeRecommendationsTest:
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_call_find_user_bookings_for_recommendation_and_not_find_from_recommendation(
        self, find_user_bookings_for_recommendation, find_from_recommendation
    ):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        stock.offerId = 1
        mediation = create_mediation(offer)
        recommendation = create_recommendation(offer, user, mediation=mediation)
        recommendation.offerId = 1
        find_user_bookings_for_recommendation.return_value = [
            create_booking(user=user, stock=stock, venue=venue, recommendation=recommendation)
        ]

        # When
        serialized_recommendations = serialize_recommendations([recommendation], user)

        # Then
        find_user_bookings_for_recommendation.assert_called_once()
        find_from_recommendation.assert_not_called()
        assert "bookings" in serialized_recommendations[0]

    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_return_dict_with_bookings_key_and_empty_list_when_no_bookings(
        self, find_user_bookings_for_recommendation
    ):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type(thumb_count=1)
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)
        stock.offerId = 1
        mediation = create_mediation(offer)
        recommendation = create_recommendation(offer, user, mediation=mediation)
        recommendation.offerId = 1
        find_user_bookings_for_recommendation.return_value = []

        # When
        serialized_recommendations = serialize_recommendations([recommendation], user)

        # Then
        assert serialized_recommendations[0]["bookings"] == []

    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_return_dict_with_bookings_key_and_empty_list_for_recommendation_without_bookings_and_with_serialized_booking_list_for_recommendation_with_booking(
        self, find_user_bookings_for_recommendation
    ):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)
        stock1.offerId = 1
        stock2.offerId = 2
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        recommendation1 = create_recommendation(offer1, user, mediation=mediation1)
        recommendation1.offerId = 1
        recommendation2 = create_recommendation(offer2, user, mediation=mediation2)
        recommendation2.offerId = 2
        find_user_bookings_for_recommendation.return_value = [
            create_booking(user=user, stock=stock2, venue=venue, recommendation=recommendation2)
        ]

        # When
        serialized_recommendations = serialize_recommendations([recommendation1, recommendation2], user)

        # Then
        assert serialized_recommendations[0]["bookings"] == []
        assert serialized_recommendations[1]["bookings"] != []
