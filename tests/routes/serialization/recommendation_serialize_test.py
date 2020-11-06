from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.recommendations.factories import RecommendationFactory
from pcapi.model_creators.generic_creators import create_booking
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.routes.serialization.recommendation_serialize import serialize_recommendation
from pcapi.routes.serialization.recommendation_serialize import serialize_recommendations


@pytest.mark.usefixtures("db_session")
class SerializeRecommendationTest:
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def test_should_return_booking_if_query_booking_is_True(self, stubed_find_from_recommendation):
        # Given
        offer = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        stock = StockFactory(offer=offer)
        recommendation = RecommendationFactory(offer=offer)
        stubed_find_from_recommendation.return_value = [
            create_booking(
                user=recommendation.user, stock=stock, venue=recommendation.offer.venue, recommendation=recommendation
            )
        ]

        # When
        serialized_recommendation = serialize_recommendation(recommendation, recommendation.user, query_booking=True)

        # Then
        assert "bookings" in serialized_recommendation
        assert serialized_recommendation["bookings"] is not None

    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def test_should_not_return_booking_if_query_booking_is_False(self, stubed_find_from_recommendation):
        # Given
        offer = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        stock = StockFactory(offer=offer)
        recommendation = RecommendationFactory(offer=offer)
        stubed_find_from_recommendation.return_value = [
            create_booking(
                user=recommendation.user, stock=stock, venue=recommendation.offer.venue, recommendation=recommendation
            )
        ]

        # When
        serialized_recommendation = serialize_recommendation(recommendation, recommendation.user, query_booking=False)

        # Then
        assert "bookings" not in serialized_recommendation

    @freeze_time("2020-09-01 00:00:00")
    @patch("pcapi.routes.serialization.recommendation_serialize.get_cancellation_limit_date")
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def should_have_a_cancellation_limit_date_when_its_an_event(
        self, stubed_find_from_recommendation, mocked_get_cancellation_limit_date
    ):
        # Given
        offer = OfferFactory(product__type=str(EventType.CINEMA))
        stock = StockFactory(offer=offer, beginningDatetime=datetime(2020, 10, 15))
        recommendation = RecommendationFactory(offer=offer)
        stubed_find_from_recommendation.return_value = [
            create_booking(
                user=recommendation.user, stock=stock, venue=recommendation.offer.venue, recommendation=recommendation
            )
        ]

        # When
        serialize_recommendation(recommendation, recommendation.user, query_booking=False)

        # Then
        mocked_get_cancellation_limit_date.assert_called_once_with("2020-10-15T00:00:00Z")

    @patch("pcapi.routes.serialization.recommendation_serialize.get_cancellation_limit_date")
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    def should_not_have_a_cancellation_limit_date_when_its_a_thing(
        self, stubed_find_from_recommendation, mocked_get_cancellation_limit_date
    ):
        # Given
        offer = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        stock = StockFactory(offer=offer)
        recommendation = RecommendationFactory(offer=offer)
        stubed_find_from_recommendation.return_value = [
            create_booking(
                user=recommendation.user, stock=stock, venue=recommendation.offer.venue, recommendation=recommendation
            )
        ]

        # When
        serialize_recommendation(recommendation, recommendation.user, query_booking=False)

        # Then
        mocked_get_cancellation_limit_date.assert_called_once_with(None)


@pytest.mark.usefixtures("db_session")
class SerializeRecommendationsTest:
    @patch("pcapi.core.bookings.repository.find_from_recommendation")
    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_call_find_user_bookings_for_recommendation_and_not_find_from_recommendation(
        self, mocked_find_user_bookings_for_recommendation, mocked_find_from_recommendation
    ):
        # Given
        offer = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        stock = StockFactory(offer=offer)
        recommendation = RecommendationFactory(offer=offer)
        mocked_find_user_bookings_for_recommendation.return_value = [
            create_booking(
                user=recommendation.user, stock=stock, venue=recommendation.offer.venue, recommendation=recommendation
            )
        ]

        # When
        serialized_recommendations = serialize_recommendations([recommendation], recommendation.user)

        # Then
        mocked_find_user_bookings_for_recommendation.assert_called_once()
        mocked_find_from_recommendation.assert_not_called()
        assert "bookings" in serialized_recommendations[0]

    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_return_dict_with_bookings_key_and_empty_list_when_no_bookings(
        self, stubed_find_user_bookings_for_recommendation
    ):
        # Given
        recommendation = RecommendationFactory(offer__product__type=str(ThingType.LIVRE_EDITION))
        stubed_find_user_bookings_for_recommendation.return_value = []

        # When
        serialized_recommendations = serialize_recommendations([recommendation], recommendation.user)

        # Then
        assert serialized_recommendations[0]["bookings"] == []

    @patch("pcapi.core.bookings.repository.find_user_bookings_for_recommendation")
    def test_should_return_dict_with_bookings_key_and_empty_list_for_recommendation_without_bookings_and_with_serialized_booking_list_for_recommendation_with_booking(
        self, mocked_find_user_bookings_for_recommendation
    ):
        # Given
        offer1 = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        StockFactory(offer=offer1)
        recommendation1 = RecommendationFactory(offer=offer1)

        offer2 = OfferFactory(product__type=str(ThingType.LIVRE_EDITION))
        stock2 = StockFactory(offer=offer2)
        recommendation2 = RecommendationFactory(offer=offer2)
        mocked_find_user_bookings_for_recommendation.return_value = [
            create_booking(
                user=recommendation2.user,
                stock=stock2,
                venue=recommendation2.offer.venue,
                recommendation=recommendation2,
            )
        ]

        # When
        serialized_recommendations = serialize_recommendations([recommendation1, recommendation2], recommendation2.user)

        # Then
        assert serialized_recommendations[0]["bookings"] == []
        assert serialized_recommendations[1]["bookings"] != []
