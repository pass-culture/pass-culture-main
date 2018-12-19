""" routes recommendations tests """
from datetime import datetime, timedelta


import pytest

from models import PcObject, \
    EventType
from tests.conftest import clean_database
from utils.date import strftime
from utils.test_utils import API_URL, \
    create_event_occurrence, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_event_occurrence, \
    create_user, \
    create_venue, \
    req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'

now = datetime.utcnow()
one_day_from_now = now + timedelta(days=1)
ten_days_from_now = now + timedelta(days=10)

@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_recommendations_in_date_range_from_search_by_date(app):
    # Given
    search = "date=" + strftime(now) + "&days=0-1"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Training in Modern Jazz')

    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    recommendations = response.json()
    assert recommendations[0]['offer']['dateRange']== [strftime(now), strftime(one_day_from_now)]
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_no_recommendation_from_search_by_date(app):
    # Given
    search = "date=" + strftime(ten_days_from_now) + "&days=0-1"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Training in Modern Jazz')

    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    recommendations = response.json()
    assert len(response.json()) == 0
