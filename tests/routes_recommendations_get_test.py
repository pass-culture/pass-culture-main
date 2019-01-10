""" routes recommendations get tests """
from datetime import datetime, timedelta

import pytest

from models import PcObject, \
    EventType, \
    Offer, \
    Recommendation
from tests.conftest import clean_database
from utils.date import strftime
from utils.test_utils import API_URL, \
    create_event_occurrence, \
    create_stock_from_event_occurrence, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock, \
    create_stock_from_offer, \
    create_thing, \
    create_thing_offer, \
    create_user, \
    create_venue, \
    req, \
    req_with_auth

now = datetime.utcnow()
one_day_from_now = now + timedelta(days=1)
ten_days_from_now = now + timedelta(days=10)

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
def test_get_recommendations_with_double_and_trailing_whitespaces_returns_one_recommendation(app):
    # given
    search = "keywords= rencontres  avec "
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
    assert len(response.json()) == 0


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_two_recommendations_from_search_by_date_and_type(app):
    # Given
    search = "categories=Lire%2CRegarder&date=" + strftime(now) + "&days=0-1"
    search = "categories=Lire%2CRegarder%2CActivation"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
    offer2 = create_event_offer(venue, event_name='Spectacle', event_type=EventType.SPECTACLE_VIVANT)
    thing = create_thing(thing_name='Lire un livre', is_national=True)

    thingOffer = create_thing_offer(venue, thing)

    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thingOffer, user)
    recommendation3 = create_recommendation(offer2, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    stock1 = create_stock_from_offer(offer2)
    thingStock = create_stock(price=12, available=5, offer=thingOffer)
    PcObject.check_and_save(stock, recommendation, recommendation2, recommendation3, thingStock, stock1)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    assert len(response.json()) == 2
    recommendations = response.json()
    assert recommendations[0]['offer']['eventOrThing']['name'] == 'The new film'
    assert recommendations[1]['offer']['eventOrThing']['name'] == 'Lire un livre'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns__recommendations_from_search_by_date_and_type_except_if_it_is_activation_type(app):
    # Given
    search = "categories=Lire%2CRegarder%2CActivation&date=" + strftime(now) + "&days=0-1"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
    offer2 = create_event_offer(venue, event_name='Activation de votre Pass Culture', event_type=EventType.ACTIVATION)
    thing = create_thing(thing_name='Lire un livre', is_national=True)

    thingOffer = create_thing_offer(venue, thing)

    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thingOffer, user)
    recommendation3 = create_recommendation(offer2, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    stock1 = create_stock_from_offer(offer2)
    thingStock = create_stock(price=12, available=5, offer=thingOffer)
    PcObject.check_and_save(stock, recommendation, recommendation2, recommendation3, thingStock, stock1)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    assert len(response.json()) == 2
    recommendations = response.json()
    assert recommendations[0]['offer']['eventOrThing']['name'] == 'The new film'
    assert recommendations[1]['offer']['eventOrThing']['name'] == 'Lire un livre'


@clean_database
@pytest.mark.standalone
@pytest.mark.skip
def test_get_recommendations_returns_recommendation_from_search_by_type_including_activation_type(app):
    # Given
    search = "categories=Activation%2CLire%2CRegarder"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
    offer1 = create_event_offer(venue, event_name='Activation de votre Pass Culture', event_type=EventType.ACTIVATION)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    recommendation1 = create_recommendation(offer1, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    stock1 = create_stock_from_offer(offer1)
    PcObject.check_and_save(stock, stock1, recommendation, recommendation1)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    assert len(response.json()) == 2
    recommendations = response.json()
    assert recommendations[0]['offer']['eventOrThing']['name'] == 'The new film'
    assert recommendations[1]['offer']['eventOrThing']['name'] == 'Activation de votre Pass Culture'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_no_recommendations_from_search_by_date_and_type_and_pagination_not_in_range(app):
    # Given
    search = "categories=Lire%2CRegarder&date=" + strftime(now) + "&days=0-1&page=2"
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
    thing = create_thing(thing_name='Lire un livre', is_national=True)

    thingOffer = create_thing_offer(venue, thing)

    event_occurrence = create_event_occurrence(offer, beginning_datetime=now, end_datetime=one_day_from_now)

    recommendation = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thingOffer, user)
    stock = create_stock_from_event_occurrence(event_occurrence)
    thingStock = create_stock(price=12, available=5, offer=thingOffer)
    PcObject.check_and_save(stock, recommendation, recommendation2, thingStock)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # When
    response = auth_request.get(RECOMMENDATION_URL + '?%s' % search)

    # Then
    assert response.status_code == 200
    assert len(response.json()) == 0
