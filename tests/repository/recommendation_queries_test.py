from datetime import datetime, timedelta

from models import Recommendation
from repository import repository
from repository.recommendation_queries import update_read_recommendations, delete_useless_recommendations
from tests.conftest import clean_database
from model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_recommendation, create_favorite, create_mediation
from model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_from_offer, \
    create_stock_with_thing_offer, create_offer_with_thing_product, create_offer_with_event_product, \
    create_event_occurrence
from utils.human_ids import humanize


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


class DeleteUselessRecommendationsTest:
    @clean_database
    def test_deletes_unread_recommendations_older_than_one_week(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        old_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=8, hours=1),
                                                   date_read=None)
        new_recommendation = create_recommendation(offer, user, date_created=today, date_read=None)
        repository.save(old_recommendation, new_recommendation)
        old_recommendation_id = old_recommendation.id

        # When
        delete_useless_recommendations()

        # Then
        recommendations = Recommendation.query.all()
        assert new_recommendation in recommendations
        recommendation_ids = [recommendation.id for recommendation in recommendations]
        assert old_recommendation_id not in recommendation_ids
        assert len(recommendations) == 1

    @clean_database
    def test_deletes_useless_recommendations_with_pagination(self, app):
        # Given
        today = datetime.utcnow()
        seventeen_days_before_today = today - timedelta(days=17)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        recommendations_to_delete = []
        for index in range(5):
            recommendations_to_delete.append(create_recommendation(offer,
                                                                   user,
                                                                   date_created=seventeen_days_before_today,
                                                                   date_read=None))
        repository.save(*recommendations_to_delete)

        # When
        delete_useless_recommendations(limit=2)

        # Then
        recommendations_count = Recommendation.query.count()
        assert recommendations_count == 0

    @clean_database
    def test_keep_read_recommendations(self, app):
        # Given
        today = datetime.utcnow()
        seventeen_days_before_today = today - timedelta(days=17)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        recommendation_to_delete = create_recommendation(offer, user, date_created=seventeen_days_before_today,
                                                         date_read=None)
        read_old_recommendation = create_recommendation(offer, user, date_created=seventeen_days_before_today,
                                                        date_read=today)
        repository.save(recommendation_to_delete, read_old_recommendation)
        recommendation_id_to_delete = recommendation_to_delete.id

        # When
        delete_useless_recommendations()

        # Then
        recommendations = Recommendation.query.all()
        recommendation_ids = [recommendation.id for recommendation in recommendations]
        assert recommendation_id_to_delete not in recommendation_ids
        assert read_old_recommendation in recommendations

    @clean_database
    def test_keep_new_recommendations(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        not_read_new_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=7),
                                                            date_read=None)
        read_new_recommendation = create_recommendation(offer, user, date_created=today, date_read=today)
        recommendation_to_delete = create_recommendation(offer, user, date_created=today - timedelta(days=9),
                                                         date_read=None)
        repository.save(not_read_new_recommendation, read_new_recommendation, recommendation_to_delete)
        recommendation_to_delete_id = recommendation_to_delete.id

        # When
        delete_useless_recommendations()

        # Then
        recommendations = Recommendation.query.all()
        assert not_read_new_recommendation in recommendations
        assert read_new_recommendation in recommendations
        recommendation_ids = [recommendation.id for recommendation in recommendations]
        assert recommendation_to_delete_id not in recommendation_ids

    @clean_database
    def test_keep_booked_recommendations(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        product_with_thing_type = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, product_with_thing_type, price=0)
        user = create_user()
        booked_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=9),
                                                      date_read=None)
        booking = create_booking(user=user, recommendation=booked_recommendation, stock=stock, venue=venue)
        recommendation_to_delete = create_recommendation(offer, user, date_created=today - timedelta(days=9),
                                                         date_read=None)
        repository.save(booking, recommendation_to_delete)
        recommendation_to_delete_id = recommendation_to_delete.id

        # When
        delete_useless_recommendations()

        # Then
        recommendations = Recommendation.query.all()
        assert booked_recommendation in recommendations
        recommendation_ids = [recommendation.id for recommendation in recommendations]
        assert recommendation_to_delete_id not in recommendation_ids

    @clean_database
    def test_keep_recommendations_linked_to_favorite_offer(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        favorite_offer = create_offer_with_thing_product(venue)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        mediation = create_mediation(offer=favorite_offer)
        favorite = create_favorite(mediation=mediation, offer=favorite_offer, user=user)
        favorite_recommendation = create_recommendation(offer=favorite_offer, user=user,
                                                        date_created=today - timedelta(days=9), date_read=None)
        recommendation_to_delete = create_recommendation(offer=offer, user=user, date_created=today - timedelta(days=9),
                                                         date_read=None)
        repository.save(favorite_recommendation, recommendation_to_delete, favorite)
        recommendation_to_delete_id = recommendation_to_delete.id

        # When
        delete_useless_recommendations()

        # Then
        recommendations = Recommendation.query.all()
        assert favorite_recommendation in recommendations
        recommendation_ids = [recommendation.id for recommendation in recommendations]
        assert recommendation_to_delete_id not in recommendation_ids
