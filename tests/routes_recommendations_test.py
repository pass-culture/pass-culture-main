from datetime import datetime, timedelta

import pytest

from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth, create_offerer, create_venue, create_event_offer, create_user, \
    create_event_occurrence, create_stock_from_event_occurrence, create_thing_offer, create_stock_from_offer, \
    create_recommendation, create_mediation

RECOMMENDATION_URL = API_URL + '/recommendations'


@pytest.mark.standalone
def test_put_recommendations_works_only_when_logged_in():
    # when
    response = req.put(RECOMMENDATION_URL)

    # then
    assert response.status_code == 401


@pytest.mark.standalone
def test_get_recommendations_works_only_when_logged_in():
    # when
    response = req.get(RECOMMENDATION_URL + '?search=Training')

    # then
    assert response.status_code == 401


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_one_recommendation_found_from_search_with_matching_case(app):
    # given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Training in Modern Jazz')
    recommendation = create_recommendation(offer, user)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?search=Training')

    # then
    recommendations = response.json()
    assert 'Training' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'Training'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_returns_one_recommendation_found_from_search_ignoring_case(app):
    # given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
    recommendation = create_recommendation(offer, user)
    stock = create_stock_from_offer(offer)
    PcObject.check_and_save(stock, recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?search=rencontres')

    # then
    recommendations = response.json()
    assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'rencontres'


@clean_database
@pytest.mark.standalone
def test_get_recommendations_does_not_return_recommendations_of_offers_with_soft_deleted_stocks(app):
    # given
    search = 'rencontres'
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_event_offer(venue, event_name='Rencontres avec des peintres')
    offer2 = create_event_offer(venue, event_name='Rencontres avec des auteurs')
    recommendation1 = create_recommendation(offer1, user, search=search)
    recommendation2 = create_recommendation(offer2, user, search=search)
    stock1 = create_stock_from_offer(offer1, price=10, soft_deleted=False)
    stock2 = create_stock_from_offer(offer1, price=20, soft_deleted=True)
    stock3 = create_stock_from_offer(offer2, price=30, soft_deleted=True)

    PcObject.check_and_save(stock1, stock2, stock3, recommendation1, recommendation2)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '?search=%s' % search)

    # then
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_put_recommendations_does_not_return_recommendations_of_offers_with_soft_deleted_stocks(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user(email='test@email.com', password='P@55w0rd')
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence1, soft_deleted=True)
    stock2 = create_stock_from_event_occurrence(event_occurrence2, soft_deleted=False)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(thing_offer1, soft_deleted=True)
    stock4 = create_stock_from_offer(thing_offer2, soft_deleted=False)
    recommendation1 = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thing_offer1, user)
    recommendation3 = create_recommendation(thing_offer2, user)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

    # When
    response = req_with_auth('test@email.com', 'P@55w0rd').put(RECOMMENDATION_URL, json={})

    # Then
    recommendation_ids = [r['id'] for r in (response.json())]
    assert humanize(recommendation1.id) in recommendation_ids
    assert humanize(recommendation2.id) not in recommendation_ids
    assert humanize(recommendation3.id) in recommendation_ids


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_nothing_if_no_stock_on_offer(app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    PcObject.check_and_save(user, offer)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 0


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_one_recommendation_for_offer_on_thing_with_free_stock_with_thumb_count(app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, thumb_count=1)
    stock = create_stock_from_offer(offer, price=0)
    PcObject.check_and_save(user, stock)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_nothing_for_offer_on_thing_with_free_stock_without_thumb_count_and_no_mediation(
        app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, thumb_count=0)
    stock = create_stock_from_offer(offer, price=0)
    PcObject.check_and_save(user, stock)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 0


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_one_recommendation_for_offer_on_thing_with_free_stock_with_mediation_but_no_thumb_count(
        app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, thumb_count=0)
    stock = create_stock_from_offer(offer, price=0)
    mediation = create_mediation(offer)
    PcObject.check_and_save(user, stock, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_nothing_for_offer_on_event_with_free_stock_if_no_mediation_and_no_thumb_count(app):
    # given
    now = datetime.utcnow()
    four_days_from_now = now + timedelta(days=4)
    eight_days_from_now = now + timedelta(days=8)

    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(
        offer,
        beginning_datetime=four_days_from_now,
        end_datetime=eight_days_from_now
    )
    stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
    PcObject.check_and_save(user, stock)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 0


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_one_recommendation_for_offer_on_event_with_free_stock_and_mediation_but_no_thumb_count(
        app):
    # given
    now = datetime.utcnow()
    four_days_from_now = now + timedelta(days=4)
    eight_days_from_now = now + timedelta(days=8)

    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(
        offer,
        beginning_datetime=four_days_from_now,
        end_datetime=eight_days_from_now
    )
    mediation = create_mediation(offer)
    stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
    PcObject.check_and_save(user, stock, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_one_recommendation_for_offer_on_event_with_free_stock_and_thumb_count_but_no_mediation(
        app):
    # given
    now = datetime.utcnow()
    four_days_from_now = now + timedelta(days=4)
    eight_days_from_now = now + timedelta(days=8)

    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, thumb_count=1, dominant_color=b'123')
    event_occurrence = create_event_occurrence(
        offer,
        beginning_datetime=four_days_from_now,
        end_datetime=eight_days_from_now
    )
    stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
    PcObject.check_and_save(user, stock)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 1


@clean_database
@pytest.mark.standalone
def test_get_favorite_recommendations_works_only_when_logged_in(app):
    # when
    response = req.get(RECOMMENDATION_URL + '/favorites')

    # then
    assert response.status_code == 401


@clean_database
@pytest.mark.standalone
def test_get_favorite_recommendations_returns_recommendations_favored_by_current_user(app):
    # given
    user1 = create_user(email='user1@test.com')
    user2 = create_user(email='user2@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_event_offer(venue)
    offer2 = create_event_offer(venue)
    recommendation1 = create_recommendation(offer1, user1, is_favorite=False)
    recommendation2 = create_recommendation(offer2, user1, is_favorite=True)
    recommendation3 = create_recommendation(offer2, user1, is_favorite=True)
    recommendation4 = create_recommendation(offer2, user2, is_favorite=True)
    PcObject.check_and_save(user1, user2, recommendation1, recommendation2, recommendation3, recommendation4)
    auth_request = req_with_auth(user1.email, user1.clearTextPassword)

    # when
    response = auth_request.get(RECOMMENDATION_URL + '/favorites')

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2
