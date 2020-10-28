from datetime import datetime

from pcapi.repository import repository
from pcapi.repository.recommendation_queries import update_read_recommendations
from tests.conftest import clean_database
from pcapi.model_creators.generic_creators import create_user, create_offerer, create_venue, \
    create_recommendation
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_from_offer, \
    create_offer_with_thing_product, create_offer_with_event_product, \
    create_event_occurrence
from pcapi.utils.human_ids import humanize


class UpdateReadRecommendationsTest:
    @clean_database
    def test_should_update_read_recommendations(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user = create_user()
        event_occurrence1 = create_event_occurrence(offer)
        event_occurrence2 = create_event_occurrence(offer)
        stock1 = create_stock_from_event_occurrence(event_occurrence1)
        stock2 = create_stock_from_event_occurrence(event_occurrence2)
        thing_offer1 = create_offer_with_thing_product(venue)
        thing_offer2 = create_offer_with_thing_product(venue)
        stock3 = create_stock_from_offer(thing_offer1)
        stock4 = create_stock_from_offer(thing_offer2)
        recommendation1 = create_recommendation(offer, user)
        recommendation2 = create_recommendation(thing_offer1, user)
        recommendation3 = create_recommendation(thing_offer2, user)
        repository.save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

        # When
        reads = [
            {"id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689Z"},
            {"id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689Z"},
            {"id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689Z"},
        ]
        update_read_recommendations(reads)

        # Then
        assert recommendation1.dateRead == datetime(2018, 12, 17, 15, 59, 11, 689000)
        assert recommendation2.dateRead == datetime(2018, 12, 17, 15, 59, 15, 689000)
        assert recommendation3.dateRead == datetime(2018, 12, 17, 15, 59, 21, 689000)

    @clean_database
    def test_should_not_update_read_recommendations_when_user_did_not_read_any_recommendation(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        recommendation = create_recommendation(offer, user)
        repository.save(stock, recommendation)

        # When
        reads = []
        update_read_recommendations(reads)

        # Then
        assert recommendation.dateRead is None
