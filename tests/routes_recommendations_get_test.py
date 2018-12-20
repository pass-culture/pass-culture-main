""" routes recommendations get tests """

import pytest

from models import PcObject, \
    EventType
from tests.conftest import clean_database
from utils.test_utils import API_URL, \
    create_event_occurrence, \
    create_stock_from_event_occurrence, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_offer, \
    create_user, \
    create_venue, \
    req, \
    req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'

@pytest.mark.standalone
def test_get_recommendations_works_only_when_logged_in():
    # when
    url = RECOMMENDATION_URL + '?keywords=Training'
    response = req.get(url, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 401


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_one_recommendation_found_from_search_with_matching_case(app):
    # given
    search = "keywords=Training"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Training in Modern Jazz')
    recommendation = create_recommendation(offer, user, search=search)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    recommendations = response.json()
    assert 'Training' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'keywords=Training'


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
def test_get_recommendations_returns_one_recommendation_found_from_search_ignoring_case(app):
    # given
    search = "keywords=rencontres"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
    # NOTE: we need to create event occurrence and stock because
    # GET recommendations filter offer without stock
    event_occurrence = create_event_occurrence(offer)
    stock = create_stock_from_event_occurrence(event_occurrence)
    recommendation = create_recommendation(offer, user, search=search)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    recommendations = response.json()
    assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'keywords=rencontres'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_one_recommendation_found_from_partial_search(app):
    # given
    search = "keywords=rencon"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
    event_occurrence = create_event_occurrence(offer)
    stock = create_stock_from_event_occurrence(event_occurrence)
    recommendation = create_recommendation(offer, user, search=search)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # then
    recommendations = response.json()
    assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'keywords=rencon'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_does_not_return_recommendations_of_offers_with_soft_deleted_stocks(app):
    # given
    search = 'keywords=rencontres'
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_event_offer(venue, event_name='Rencontres avec des peintres')
    offer2 = create_event_offer(venue, event_name='Rencontres avec des auteurs')
    recommendation1 = create_recommendation(offer1, user, search=search)
    recommendation2 = create_recommendation(offer2, user, search=search)

    # NOTE: we need to create event occurrence and stock because
    # GET recommendations filter offer without stock
    event_occurrence1 = create_event_occurrence(offer1)
    event_occurrence2 = create_event_occurrence(offer1)
    event_occurrence3 = create_event_occurrence(offer2)

    stock1 = create_stock_from_event_occurrence(event_occurrence1, price=10, soft_deleted=False)
    stock2 = create_stock_from_event_occurrence(event_occurrence2, price=20, soft_deleted=True)
    stock3 = create_stock_from_event_occurrence(event_occurrence3, price=30, soft_deleted=True)

    PcObject.check_and_save(stock1, stock2, stock3, recommendation1, recommendation2)
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
