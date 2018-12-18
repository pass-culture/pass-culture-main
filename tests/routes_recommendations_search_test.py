""" routes recommendations tests """

import pytest

from models import PcObject, \
    EventType
from tests.conftest import clean_database
from utils.test_utils import API_URL, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_offer, \
    create_user, \
    create_venue, \
    req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_one_recommendation_from_search_by_type(app):
    # given
    search = "categories=Applaudir"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Training in Modern Jazz')
    recommendation = create_recommendation(offer, user)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_two_recommendation_from_filter_by_two_types(app):
    # given
    search = "categories=Applaudir%2CRegarder"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_event_offer(venue, event_name='Training in Modern Jazz')
    offer2 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)
    recommendation = create_recommendation(offer1, user)
    recommendation2 = create_recommendation(offer2, user)
    stock = create_stock_from_offer(offer1)
    stock2 = create_stock_from_offer(offer2)
    PcObject.check_and_save(stock, recommendation, stock2, recommendation2)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    assert len(response.json()) == 2


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_all_recommendations_from_filter_by_all_types(app):
    # given
    search = "categories=%25C3%2589couter%2CApplaudir%2CJouer%2CLire%2CPratiquer%2CRegarder%2CRencontrer"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_event_offer(venue, event_name='Training in Modern Jazz')
    offer2 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)
    offer3 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.SPECTACLE_VIVANT)
    recommendation = create_recommendation(offer1, user)
    recommendation2 = create_recommendation(offer2, user)
    recommendation3 = create_recommendation(offer3, user)
    stock = create_stock_from_offer(offer1)
    stock2 = create_stock_from_offer(offer2)
    stock3 = create_stock_from_offer(offer3)
    PcObject.check_and_save(stock, recommendation, stock2, recommendation2, stock3, recommendation3)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    assert len(response.json()) == 3
