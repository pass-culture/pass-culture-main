from datetime import datetime

from dateutil.tz import tzutc
from freezegun import freeze_time

from models import PcObject
from models.db import db
from recommendations_engine import create_recommendations_for_discovery, \
    get_recommendation_search_params, \
    give_requested_recommendation_to_user
from tests.conftest import clean_database
from tests.test_utils import create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_offer, \
    create_offer_with_thing_product, \
    create_user, \
    create_venue
from utils.date import strftime
from utils.human_ids import humanize


class GiveRequestedRecommendationToUserTest:
    @clean_database
    def test_when_recommendation_exists_returns_it(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_ok = create_offer_with_thing_product(venue, thumb_count=0)
        stock = create_stock_from_offer(offer_ok, price=0)
        mediation = create_mediation(offer_ok, is_active=False)
        reco_ok = create_recommendation(offer=offer_ok, user=user, mediation=mediation)
        PcObject.save(reco_ok, stock)

        # When
        result_reco = give_requested_recommendation_to_user(
            user, offer_ok.id, mediation.id)

        # Then
        assert result_reco.id == reco_ok.id

    @clean_database
    def test_when_recommendation_exists_for_other_user_returns_a_new_one_for_the_current_user(self, app):
        # Given
        user = create_user()
        user2 = create_user(email='john.doe2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_ok = create_offer_with_thing_product(venue, thumb_count=0)
        stock = create_stock_from_offer(offer_ok, price=0)
        mediation = create_mediation(offer_ok, is_active=False)
        reco_ko = create_recommendation(offer=offer_ok, user=user, mediation=mediation)
        PcObject.save(reco_ko, stock, user2)

        # When
        result_reco = give_requested_recommendation_to_user(
            user2, offer_ok.id, mediation.id)

        # Then
        assert result_reco.id != reco_ko.id
        assert result_reco.offerId == offer_ok.id
        assert result_reco.mediationId == mediation.id
        assert result_reco.userId == user2.id


class GetRecommendationSearchParamsTest:
    def test_when_days_0_1_returns_days_intervals_between_date_and_date_in_one_day(self, app):
        # Given
        request_args = {
            'days': '0-1',
            'date': '2019-01-31T12:00:00+00:00'
        }

        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 1, 31, 12, 0, tzinfo=tzutc()), datetime(2019, 2, 1, 12, 0, tzinfo=tzutc())]]}

    def test_when_days_1_5_returns_days_intervals_between_date_in_one_day_and_date_in_five_days(self, app):
        # Given
        request_args = {
            'days': '1-5',
            'date': '2019-01-31T12:00:00+00:00'
        }

        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 2, 1, 12, 0, tzinfo=tzutc()), datetime(2019, 2, 5, 12, 0, tzinfo=tzutc())]]}

    def test_when_days_more_than_5_returns_days_intervals_between_date_with_days_and_date_in_100000_days(
            self, app):
        # Given
        request_args = {
            'days': '5-100000',
            'date': '2019-01-31T12:00:00+00:00'
        }

        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 2, 5, 12, 0, tzinfo=tzutc()), datetime(2292, 11, 15, 12, 0, tzinfo=tzutc())]]}


@clean_database
def test_create_recommendations_for_discovery_does_not_put_mediation_ids_of_inactive_mediations(app):
    # Given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_offer_with_thing_product(venue, thumb_count=0)
    stock1 = create_stock_from_offer(offer1, price=0)
    mediation1 = create_mediation(offer1, is_active=False)
    offer2 = create_offer_with_thing_product(venue, thumb_count=0)
    stock2 = create_stock_from_offer(offer2, price=0)
    mediation2 = create_mediation(offer2, is_active=False)
    mediation3 = create_mediation(offer2, is_active=True)
    PcObject.save(user, stock1, mediation1, stock2, mediation2, mediation3)

    # When
    recommendations = create_recommendations_for_discovery(user=user)

    # Then
    mediations = list(map(lambda x: x.mediationId, recommendations))
    assert len(recommendations) == 1
    assert mediation3.id in mediations
    assert humanize(mediation2.id) not in mediations
    assert humanize(mediation1.id) not in mediations


@clean_database
def test_create_recommendations_for_discovery_should_include_recommendations_on_offers_previously_displayed_in_search_results(
        app):
    # Given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_offer_with_thing_product(venue, thumb_count=0)
    stock1 = create_stock_from_offer(offer1, price=0)
    mediation1 = create_mediation(offer1, is_active=True)
    offer2 = create_offer_with_thing_product(venue, thumb_count=0)
    stock2 = create_stock_from_offer(offer2, price=0)
    mediation2 = create_mediation(offer2, is_active=True)

    recommendation = create_recommendation(offer=offer2, user=user, mediation=mediation2, search="bla")

    PcObject.save(user, stock1, mediation1, stock2, mediation2, recommendation)
    db.session.refresh(offer2)

    # When
    recommendations = create_recommendations_for_discovery(user=user)

    # Then
    assert len(recommendations) == 2
