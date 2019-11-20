from datetime import datetime, timedelta

from models import PcObject, Recommendation
from repository.recommendation_queries import keep_only_bookable_stocks, \
    update_read_recommendations, delete_all_unread_recommendations_older_than_one_week
from tests.conftest import clean_database
from tests.test_utils import create_recommendation, create_offer_with_event_product, create_offerer, \
    create_venue, create_user, create_stock_from_event_occurrence, create_event_occurrence, create_stock_from_offer, \
    create_offer_with_thing_product, create_mediation, create_booking, create_stock_with_thing_offer, create_favorite

from utils.human_ids import humanize


@clean_database
def test_filter_out_recommendation_with_not_bookable_stocks_returns_recos_with_at_least_one_not_soft_deleted_stock(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    user = create_user()

    event_offer = create_offer_with_event_product(venue)
    soft_deleted_thing_offer = create_offer_with_thing_product(venue)
    active_thing_offer = create_offer_with_thing_product(venue)

    event_occurrence1 = create_event_occurrence(event_offer)
    event_occurrence2 = create_event_occurrence(event_offer)

    active_thing_stock = create_stock_from_offer(active_thing_offer)
    active_event_stock = create_stock_from_event_occurrence(event_occurrence2)
    soft_deleted_event_stock = create_stock_from_event_occurrence(event_occurrence1)
    soft_deleted_event_stock.isSoftDeleted = True
    soft_deleted_thing_stock = create_stock_from_offer(soft_deleted_thing_offer)
    soft_deleted_thing_stock.isSoftDeleted = True

    recommendation_on_active_thing_stock = create_recommendation(active_thing_offer, user)
    recommendation_on_both_soft_deleted_and_active_event_stocks = create_recommendation(event_offer, user)
    recommendation_on_soft_deleted_thing_stock = create_recommendation(soft_deleted_thing_offer, user)

    PcObject.save(soft_deleted_event_stock, active_event_stock, soft_deleted_thing_stock, active_thing_stock,
                  recommendation_on_both_soft_deleted_and_active_event_stocks,
                  recommendation_on_soft_deleted_thing_stock, recommendation_on_active_thing_stock)

    # When
    result = keep_only_bookable_stocks().all()

    # Then
    recommendation_ids = [r.id for r in result]
    assert recommendation_on_both_soft_deleted_and_active_event_stocks.id in recommendation_ids
    assert recommendation_on_soft_deleted_thing_stock.id not in recommendation_ids
    assert recommendation_on_active_thing_stock.id in recommendation_ids


@clean_database
def test_filter_out_recommendation_with_not_bookable_stocks_returns_recos_with_valid_booking_date(app):
    # Given
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    tomorrow = datetime.utcnow() + timedelta(days=1)

    offerer = create_offerer()
    venue = create_venue(offerer)
    user = create_user()

    invalid_booking_date_offer = create_offer_with_thing_product(venue)
    valid_booking_date_offer = create_offer_with_thing_product(venue)

    invalid_booking_date_stock = create_stock_from_offer(invalid_booking_date_offer, booking_limit_datetime=one_day_ago)
    valid_booking_date_stock_valid = create_stock_from_offer(valid_booking_date_offer, booking_limit_datetime=tomorrow)
    valid_booking_date_stock_invalid = create_stock_from_offer(valid_booking_date_offer,
                                                               booking_limit_datetime=one_day_ago)

    recommendation_on_invalid_booking_date_stock = create_recommendation(invalid_booking_date_offer, user)
    recommendation_on_valid_booking_date_stock = create_recommendation(valid_booking_date_offer, user)

    PcObject.save(invalid_booking_date_stock, recommendation_on_invalid_booking_date_stock,
                  recommendation_on_valid_booking_date_stock, valid_booking_date_stock_valid,
                  valid_booking_date_stock_invalid)

    # When
    result = keep_only_bookable_stocks().all()

    # Then
    recommendation_ids = [r.id for r in result]
    assert len(recommendation_ids) == 1
    assert recommendation_on_valid_booking_date_stock.id in recommendation_ids


@clean_database
def test_update_read_recommendations(app):
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
    PcObject.save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

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


class DeleteAllUnreadRecommendationsOlderThanOneWeekTest:
    @clean_database
    def test_deletes_unread_recommendations_older_than_one_week(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        old_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=8), date_read=None)
        new_recommendation = create_recommendation(offer, user, date_created=today, date_read=None)
        PcObject.save(old_recommendation, new_recommendation)

        # When
        delete_all_unread_recommendations_older_than_one_week()

        # Then
        recommendations = Recommendation.query.all()
        assert new_recommendation in recommendations
        assert old_recommendation not in recommendations

    @clean_database
    def test_deletes_unread_recommendations_older_than_one_week_with_pagination(self, app):
        # Given
        today = datetime.utcnow()
        seventeen_days_before_today = today - timedelta(days=17)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        recommendations_to_delete = []
        i = 0
        while i < 100:
            recommendations_to_delete.append(create_recommendation(offer,
                                                                   user,
                                                                   date_created=seventeen_days_before_today,
                                                                   date_read=None))
            i += 1
        PcObject.save(*recommendations_to_delete)

        # When
        delete_all_unread_recommendations_older_than_one_week(per_page=10)

        # Then
        recommendations = Recommendation.query.all()
        assert len(recommendations) == 0


    @clean_database
    def test_doesnt_delete_read_recommendations_older_than_one_week(self, app):
        # Given
        today = datetime.utcnow()
        seventeen_days_before_today = today - timedelta(days=17)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        not_read_old_recommendation = create_recommendation(offer, user, date_created=seventeen_days_before_today, date_read=None)
        read_old_recommendation = create_recommendation(offer, user, date_created=seventeen_days_before_today, date_read=today)
        PcObject.save(not_read_old_recommendation, read_old_recommendation)

        # When
        delete_all_unread_recommendations_older_than_one_week()

        # Then
        recommendations = Recommendation.query.all()
        assert not_read_old_recommendation not in recommendations
        assert read_old_recommendation in recommendations


    @clean_database
    def test_doesnt_delete_new_recommendations(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        not_read_new_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=7),
                                                            date_read=None)
        read_new_recommendation = create_recommendation(offer, user, date_created=today, date_read=today)
        to_delete_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=9), date_read=None)
        PcObject.save(not_read_new_recommendation, read_new_recommendation, to_delete_recommendation)

        # When
        delete_all_unread_recommendations_older_than_one_week()

        # Then
        recommendations = Recommendation.query.all()
        assert not_read_new_recommendation in recommendations
        assert read_new_recommendation in recommendations
        assert to_delete_recommendation not in recommendations

    @clean_database
    def test_doesnt_delete_booked_recommendations(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        product_with_thing_type = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, product_with_thing_type, price=0)
        user = create_user()
        booked_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=9), date_read=None)
        booking = create_booking(user, stock=stock,  venue=venue, recommendation=booked_recommendation)
        to_delete_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=9), date_read=None)
        PcObject.save(booking, to_delete_recommendation)

        # When
        delete_all_unread_recommendations_older_than_one_week()

        # Then
        recommendations = Recommendation.query.all()
        assert booked_recommendation in recommendations
        assert to_delete_recommendation not in recommendations


    @clean_database
    def test_doesnt_delete_recommendations_linked_to_favorite_offer(self, app):
        # Given
        today = datetime.utcnow()
        offerer = create_offerer()
        venue = create_venue(offerer)
        favorite_offer = create_offer_with_thing_product(venue)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        mediation = create_mediation(favorite_offer)
        favorite = create_favorite(mediation, favorite_offer, user)
        favorite_recommendation = create_recommendation(favorite_offer, user, date_created=today - timedelta(days=9), date_read=None)
        to_delete_recommendation = create_recommendation(offer, user, date_created=today - timedelta(days=9), date_read=None)
        PcObject.save(favorite_recommendation, to_delete_recommendation, favorite)

        # When
        delete_all_unread_recommendations_older_than_one_week()

        # Then
        recommendations = Recommendation.query.all()
        assert favorite_recommendation in recommendations
        assert to_delete_recommendation not in recommendations

