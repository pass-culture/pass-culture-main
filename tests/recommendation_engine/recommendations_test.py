import pytest
from datetime import datetime
from dateutil.tz import tzlocal
from freezegun import freeze_time

from models import PcObject
from models.db import db
from recommendations_engine import create_recommendations_for_discovery, \
    get_recommendation_search_params
from tests.conftest import clean_database
from utils.date import strftime
from utils.human_ids import humanize
from tests.test_utils import create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_offer, \
    create_offer_with_thing_product, \
    create_user, \
    create_venue


@clean_database
@pytest.mark.standalone
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


@freeze_time('2019-01-31 12:00:00')
@pytest.mark.standalone
class GetRecommendationSearchParamsTest:
    def setup_class(self):
        self.now = datetime.utcnow()

    def test_when_days_0_1_and_date_today_returns_dictionary_with_days_intervals_today_and_in_one_day(self):
        # Given
        request_args = {'days': '0-1', 'date': strftime(self.now)}
        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 1, 31, 12, 0, tzinfo=tzlocal()), datetime(2019, 2, 1, 12, 0, tzinfo=tzlocal())]]}

    def test_when_days_1_5_and_date_today_returns_dictionary_with_days_intervals_in_one_day_and_in_five_days(self):
        # Given
        request_args = {'days': '1-5', 'date': strftime(self.now)}
        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 2, 1, 12, 0, tzinfo=tzlocal()), datetime(2019, 2, 5, 12, 0, tzinfo=tzlocal())]]}

    def test_when_days_more_than_5_and_date_today_returns_dictionary_with_days_intervals_in_five_days_and_100000_days(self):
        # Given
        request_args = {'days': '5-100000', 'date': strftime(self.now)}
        # When
        search_params = get_recommendation_search_params(request_args)

        # Then
        assert search_params == {'days_intervals': [
            [datetime(2019, 2, 5, 12, 0, tzinfo=tzlocal()), datetime(2292, 11, 15, 12, 0, tzinfo=tzlocal())]]}


@clean_database
@pytest.mark.standalone
def test_create_recommendations_for_discovery_should_include_recommendations_on_offers_previously_displayed_in_search_results(app):
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
