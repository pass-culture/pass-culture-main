""" routes recommendations tests """
from datetime import datetime, timedelta

import pytest

from models import PcObject
from models.mediation import Mediation, upsertTutoMediations
from models.recommendation import Recommendation
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, \
    create_event_occurrence, \
    create_event_offer, \
    create_mediation, \
    create_offerer, \
    create_recommendation, \
    create_stock_from_event_occurrence, \
    create_stock_from_offer, \
    create_thing_offer, \
    create_user, \
    create_venue, \
    req, \
    req_with_auth, create_stock_with_thing_offer

RECOMMENDATION_URL = API_URL + '/recommendations'


@pytest.mark.standalone
def test_put_recommendations_works_only_when_logged_in():
    # when
    response = req.put(
        RECOMMENDATION_URL,
        headers={'origin': 'http://localhost:3000'}
    )

    # then
    assert response.status_code == 401


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
    response = req.get(RECOMMENDATION_URL + '/favorites', headers={'origin': 'http://localhost:3000'})

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


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_requested_recommendation_first(app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_thing_offer(venue, thumb_count=1)
    offer2 = create_event_offer(venue, thumb_count=1)
    offer3 = create_thing_offer(venue, thumb_count=1)
    offer4 = create_thing_offer(venue, thumb_count=1)
    now = datetime.utcnow()
    fifteen_min_ago = now - timedelta(minutes=15)
    event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                               end_datetime=now + timedelta(hours=74))
    mediation = create_mediation(offer2)
    stock1 = create_stock_from_offer(offer1, price=0)
    stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10, soft_deleted=False,
                                                booking_limit_date=now + timedelta(days=3))
    stock3 = create_stock_from_offer(offer3, price=0)
    stock4 = create_stock_from_offer(offer4, price=0)
    recommendation_offer3 = create_recommendation(offer3, user)
    recommendation_offer4 = create_recommendation(offer4, user, date_read=now - timedelta(days=1))
    PcObject.check_and_save(user, stock1, stock2, stock3, stock4, mediation, event_occurrence, recommendation_offer3,
                            recommendation_offer4)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id), json=data)

    # then
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 4
    offer_ids = set(map(lambda x: x['offer']['id'], response_json))
    recommendation_ids = set(map(lambda x: x['id'], response_json))
    assert response_json[0]['offer']['id'] == humanize(offer1.id)
    assert humanize(offer1.id) in offer_ids
    assert humanize(offer2.id) in offer_ids
    assert humanize(offer3.id) in offer_ids
    assert humanize(recommendation_offer4.id) in recommendation_ids
    assert humanize(recommendation_offer3.id) in recommendation_ids


@clean_database
@pytest.mark.standalone
def test_put_recommendations_creates_new_recommendation_when_existing_ones_invalid(app):
    # given
    now = datetime.utcnow()
    fifteen_min_ago = now - timedelta(minutes=15)
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_thing_offer(venue, thumb_count=1)
    offer2 = create_event_offer(venue, thumb_count=1)
    offer3 = create_thing_offer(venue, thumb_count=1)
    offer4 = create_thing_offer(venue, thumb_count=1)
    event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                               end_datetime=now + timedelta(hours=74))
    mediation = create_mediation(offer2)
    stock1 = create_stock_from_offer(offer1, price=0)
    stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10, soft_deleted=False,
                                                booking_limit_date=now + timedelta(days=3))
    stock3 = create_stock_from_offer(offer3, price=0)
    stock4 = create_stock_from_offer(offer4, price=0)
    recommendation_offer1 = create_recommendation(offer1, user, valid_until_date=fifteen_min_ago)
    recommendation_offer2 = create_recommendation(offer2, user, valid_until_date=fifteen_min_ago)
    recommendation_offer3 = create_recommendation(offer3, user, valid_until_date=fifteen_min_ago)
    recommendation_offer4 = create_recommendation(offer4, user, date_read=now - timedelta(days=1),
                                                  valid_until_date=fifteen_min_ago)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, mediation, event_occurrence, recommendation_offer3,
                            recommendation_offer4, recommendation_offer1, recommendation_offer2)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id), json=data)

    # then
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 4
    recommendation_ids = set(map(lambda x: x['id'], response_json))
    assert humanize(recommendation_offer1.id) not in recommendation_ids
    assert humanize(recommendation_offer2.id) not in recommendation_ids
    assert humanize(recommendation_offer3.id) not in recommendation_ids
    assert humanize(recommendation_offer4.id) not in recommendation_ids


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_two_recommendations_with_one_event_and_one_thing(app):
    # given
    now = datetime.utcnow()
    four_days_from_now = now + timedelta(days=4)
    eight_days_from_now = now + timedelta(days=8)
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_event = create_event_offer(venue, thumb_count=1, dominant_color=b'123')
    event_occurrence = create_event_occurrence(
        offer_event,
        beginning_datetime=four_days_from_now,
        end_datetime=eight_days_from_now
    )
    event_stock = create_stock_from_event_occurrence(event_occurrence, price=0, available=20)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    PcObject.check_and_save(user, event_stock, stock_thing)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_offer_and_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    mediation = create_mediation(offer_thing)
    PcObject.check_and_save(user, stock_thing, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                humanize(offer_thing.id) +
                                "&mediationId=" +
                                humanize(mediation.id), json={'seenRecommendationIds': []})
    # then
    assert response.status_code == 200
    recos = response.json()
    assert recos[0]['mediationId'] == humanize(mediation.id)


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_only_offer_and_no_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    mediation = create_mediation(offer_thing)
    PcObject.check_and_save(user, stock_thing, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                humanize(offer_thing.id), json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    recos = response.json()
    assert recos[0]['mediationId'] == humanize(mediation.id)


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_no_offer_and_only_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    mediation = create_mediation(offer_thing)
    PcObject.check_and_save(user, stock_thing, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?mediationId=" +
                                humanize(mediation.id), json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 200
    recos = response.json()
    assert recos[0]['offerId'] == humanize(offer_thing.id)


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_404_for_given_offer_and_mediation_but_from_different_event(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing_1 = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    offer_thing_2 = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing_1 = create_stock_with_thing_offer(offerer, venue, offer_thing_1, price=0)
    stock_thing_2 = create_stock_with_thing_offer(offerer, venue, offer_thing_2, price=0)
    mediation_1 = create_mediation(offer_thing_1)
    mediation_2 = create_mediation(offer_thing_2)
    PcObject.check_and_save(user, stock_thing_1, stock_thing_2, mediation_1, mediation_2)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                humanize(offer_thing_1.id) +
                                "?mediationId=" +
                                humanize(mediation_2.id), json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_404_for_unknown_offer_and_known_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    mediation = create_mediation(offer_thing)
    PcObject.check_and_save(user, stock_thing, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                "ABCDE" +
                                "?mediationId=" +
                                humanize(mediation.id), json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_404_for_known_offer_and_unknown_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_thing = create_thing_offer(venue, thumb_count=1, dominant_color=b'123')
    stock_thing = create_stock_with_thing_offer(offerer, venue, offer_thing, price=0)
    mediation = create_mediation(offer_thing)
    PcObject.check_and_save(user, stock_thing, mediation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                humanize(offer_thing.id) +
                                "?mediationId=" +
                                "ABCDE", json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_404_for_unknown_offer_and_unknown_mediation(app):
    # given
    user = create_user(email='user1@user.fr', password='P@55w0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL +
                                "?offerId=" +
                                "ABCDE" +
                                "?mediationId=" +
                                "ABCDE", json={'seenRecommendationIds': []})

    # then
    assert response.status_code == 404


@pytest.mark.standalone
@clean_database
def test_put_recommendations_does_not_create_recommendations_for_offers_from_non_validated_venues(app):
    # Given
    offerer = create_offerer()
    venue_not_validated = create_venue(offerer, siret=None, comment='random reason')
    venue_not_validated.generate_validation_token()
    venue_validated = create_venue(offerer, siret=None, comment='random reason')
    offer_venue_not_validated = create_thing_offer(venue_not_validated, thumb_count=1)
    offer_venue_validated = create_thing_offer(venue_validated, thumb_count=1)
    stock_venue_not_validated = create_stock_from_offer(offer_venue_not_validated)
    stock_venue_validated = create_stock_from_offer(offer_venue_validated)
    user = create_user(email='test@email.com', password='P@55w0rd')
    PcObject.check_and_save(stock_venue_not_validated, stock_venue_validated, user)
    auth_request = req_with_auth(user.email, user.clearTextPassword)
    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL, json=data)

    # Then
    assert response.status_code == 200
    recommendations = response.json()
    venue_ids = set(map(lambda x: x['offer']['venue']['id'], recommendations))
    assert humanize(venue_validated.id) in venue_ids
    assert humanize(venue_not_validated.id) not in venue_ids


@clean_database
@pytest.mark.standalone
def test_put_recommendations_does_not_return_requested_recommendation_for_offer_with_not_validated_venue(app):
    # given
    user = create_user(email='weird.bug@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue.generate_validation_token()
    offer1 = create_thing_offer(venue, thumb_count=1)
    stock1 = create_stock_from_offer(offer1, price=0)
    PcObject.check_and_save(user, stock1)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL + '?offerId=%s' % humanize(offer1.id), json=data)

    # then
    assert response.status_code == 404


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_active_mediation_only(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_thing_offer(venue, thumb_count=0)
    stock1 = create_stock_from_offer(offer1, price=0)
    mediation1 = create_mediation(offer1, is_active=False)
    offer2 = create_thing_offer(venue, thumb_count=0)
    stock2 = create_stock_from_offer(offer2, price=0)
    mediation2 = create_mediation(offer2, is_active=False)
    mediation3 = create_mediation(offer2, is_active=True)
    PcObject.check_and_save(user, stock1, mediation1, stock2, mediation2, mediation3)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL, json=data)

    # then
    assert response.status_code == 200
    json = response.json()
    mediation_ids = list(map(lambda x: x['mediationId'], json))
    assert humanize(mediation3.id) in mediation_ids
    assert humanize(mediation2.id) not in mediation_ids
    assert humanize(mediation1.id) not in mediation_ids


@clean_database
@pytest.mark.standalone
def test_put_recommendations_returns_new_recommendation_with_active_mediation_for_already_existing_but_invalid_recommendations(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_thing_offer(venue, thumb_count=0)
    stock1 = create_stock_from_offer(offer1, price=0)
    inactive_mediation = create_mediation(offer1, is_active=False)
    active_mediation = create_mediation(offer1, is_active=True)
    invalid_recommendation = create_recommendation(offer1, user, inactive_mediation,
                                           valid_until_date=datetime.utcnow() - timedelta(hours=2))
    PcObject.check_and_save(user, stock1, inactive_mediation, active_mediation, invalid_recommendation)
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    data = {'seenRecommendationIds': []}
    # when
    response = auth_request.put(RECOMMENDATION_URL, json=data)

    # then
    assert response.status_code == 200
    json = response.json()
    mediation_ids = list(map(lambda x: x['mediationId'], json))
    assert humanize(active_mediation.id) in mediation_ids
    assert humanize(inactive_mediation.id) not in mediation_ids

@clean_database
@pytest.mark.standalone
def test_put_recommendations_updates_read_recommendations(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user()
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence1)
    stock2 = create_stock_from_event_occurrence(event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(thing_offer1)
    stock4 = create_stock_from_offer(thing_offer2)
    recommendation1 = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thing_offer1, user)
    recommendation3 = create_recommendation(thing_offer2, user)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

    auth_request = req_with_auth(user.email, user.clearTextPassword)

    reads = [
        { "id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689000Z" },
        { "id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689000Z" },
        { "id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689000Z" },
    ]
    data = {'readRecommendations': reads}
    # when
    response = auth_request.put(RECOMMENDATION_URL, json=data)

    # then
    assert response.status_code == 200
    previous_date_reads = set([r['dateRead'] for r in reads])
    next_date_reads = set([r['dateRead'] for r in response.json()])
    assert previous_date_reads.issubset(next_date_reads)

@clean_database
@pytest.mark.standalone
def test_put_recommendations_at_first_request_returns_tutos(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user()
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence1)
    stock2 = create_stock_from_event_occurrence(event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(thing_offer1)
    stock4 = create_stock_from_offer(thing_offer2)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, user)
    upsertTutoMediations()

    # when
    auth_request = req_with_auth(user.email, user.clearTextPassword)
    response = auth_request.put(RECOMMENDATION_URL, json={})

    # then
    assert response.status_code == 200
    recommendations = response.json()
    assert recommendations[0]['mediation']['tutoIndex'] == 0
    assert recommendations[1]['mediation']['tutoIndex'] == 1

@clean_database
@pytest.mark.standalone
def test_put_recommendations_with_read_tuto_recommendations_returns_recommendations_without_tutos(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user()
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence1)
    stock2 = create_stock_from_event_occurrence(event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(thing_offer1)
    stock4 = create_stock_from_offer(thing_offer2)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, user)
    upsertTutoMediations()
    tuto_mediation0 = Mediation.query.filter_by(tutoIndex=0).one()
    tuto_mediation1 = Mediation.query.filter_by(tutoIndex=1).one()
    tuto_recommendation0 = create_recommendation(
        mediation=tuto_mediation0,
        user=user
    )
    tuto_recommendation1 = create_recommendation(
        mediation=tuto_mediation1,
        user=user
    )
    PcObject.check_and_save(tuto_recommendation0, tuto_recommendation1)
    humanized_tuto_recommendation0_id = humanize(tuto_recommendation0.id)
    humanized_tuto_recommendation1_id = humanize(tuto_recommendation1.id)
    reads = [
        {
            "id": humanized_tuto_recommendation0_id,
            "dateRead":  "2018-12-17T15:59:11.689Z"
        },
        {
            "id": humanized_tuto_recommendation1_id,
            "dateRead":  "2018-12-17T15:59:15.689Z"
        }
    ]
    data = { 'readRecommendations': reads }
    auth_request = req_with_auth(user.email, user.clearTextPassword)

    # when
    response = auth_request.put(RECOMMENDATION_URL, json=data)

    # then
    assert response.status_code == 200
    recommendations = response.json()
    recommendation_ids = [r['id'] for r in recommendations]
    assert humanized_tuto_recommendation0_id not in recommendation_ids
    assert humanized_tuto_recommendation1_id not in recommendation_ids
