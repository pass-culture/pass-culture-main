""" recommendations """
from collections import Counter
from datetime import datetime

import pytest
from dateutil.parser import parse as parse_date

from models import PcObject
from tests.conftest import clean_database
from utils.config import BLOB_SIZE
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth, create_offerer, create_venue, create_event_offer, create_user, \
    create_event_occurrence, create_stock_from_event_occurrence, create_thing_offer, create_stock_from_offer, \
    create_recommendation

RECOMMENDATION_URL = API_URL + '/recommendations'


def assert_no_duplicate_mediations(recos):
    mediation_ids = map(lambda recommendation: recommendation['mediationId'], recos)
    ids = list(filter(lambda mediation_id: mediation_id is not None, mediation_ids))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0


def assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos):
    recos_without_tutos = [r for r in recos if 'mediation' in r and 'tutoIndex' not in r['mediation']]
    for reco in recos_without_tutos:
        if not reco['event']['isNational']:
            assert reco.offer.venue.departementCode == '93'


def assert_no_mediations_with_stock_past_their_booking_limit(recos):
    recos_without_tutos = [r for r in recos if 'mediation' in r and 'tutoIndex' not in r['mediation']]
    for reco in recos_without_tutos:
        assert not all([
            stock['bookingLimitDatetime'] is not None
            and parse_date(stock['bookingLimitDatetime']) <= datetime.utcnow()
            for stock in oc['stocks'] for oc in reco['mediatedOccurrences']]
        )


def subtest_recos_with_params(params,
                              expected_status=200,
                              expected_mediation_id=None,
                              expected_offer_id=None,
                              is_tuto=False):
    response = req_with_auth().put(RECOMMENDATION_URL + '?' + params, json={})
    assert response.status_code == expected_status
    recos = response.json()
    assert len(recos) <= BLOB_SIZE + (2 if expected_mediation_id is None else 3)
    recos_for_tutos = filter(lambda reco: 'mediation' in reco and reco['mediation']['tutoIndex'] is not None, recos)
    assert len(list(recos_for_tutos)) == (1 if is_tuto else 0)

    if expected_mediation_id:
        assert recos[0]['mediationId'] == expected_mediation_id

    if expected_offer_id:
        assert recos[0]['offerId'] == expected_offer_id

    assert_no_mediations_with_stock_past_their_booking_limit(recos)
    assert_no_duplicate_mediations(recos)
    assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos)
    return recos


@pytest.mark.standalone
def test_put_recommendations_works_only_when_logged_in():
    # when
    response = req.put(RECOMMENDATION_URL)

    # then
    assert response.status_code == 401


def test_put_recommendations_returns_a_list_of_recos_starting_with_two_tutos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert recos[0]['mediation']['tutoIndex'] == 0
    assert recos[1]['mediation']['tutoIndex'] == 1
    recos_with_tutos = filter(lambda reco: 'mediation' in reco and reco['mediation']['tutoIndex'] is not None, recos)
    assert len(list(recos_with_tutos)) == 2


def test_put_recommendations_returns_a_list_of_48_recos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert response.status_code == 200
    assert len(recos) == 48


def test_put_recommendations_returns_no_duplicate_mediations_in_recos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert_no_duplicate_mediations(recos)


def test_put_recommendations_returns_no_recos_with_mediations_with_stock_past_their_booking_limit():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert_no_mediations_with_stock_past_their_booking_limit(recos)


def test_put_recommendations_returns_recos_with_venues_in_93_if_event_is_not_national():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos)


def test_put_recommendations_returns_at_least_one_reco_with_mediation_and_offer():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos = response.json()
    assert len(list(filter(lambda reco: 'mediationId' in reco and 'offerId' in reco, recos))) > 0


def test_put_recommendations_returns_recos_in_identical_orders():
    # given
    response1 = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})
    recos1 = response1.json()

    # when
    response2 = req_with_auth().put(RECOMMENDATION_URL, json={'seenOfferIds': []})

    # then
    recos2 = response2.json()
    assert len(recos1) == len(recos2)
    assert any([recos1[i]['id'] != recos2[i]['id'] for i in range(2, len(recos1))])


def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_offer_and_mediation(app):
    subtest_recos_with_params('offerId=AFQA&mediationId=AM',  # AM=3 AFQA=352
                              expected_status=200,
                              expected_mediation_id='AM',
                              expected_offer_id='AFQA')


def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_only_offer_and_no_mediation():
    subtest_recos_with_params('offerId=AFQA',
                              expected_status=200,
                              expected_mediation_id='AM',
                              expected_offer_id='AFQA')


def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_no_offer_and_only_mediation():
    subtest_recos_with_params('mediationId=AM',
                              expected_status=200,
                              expected_mediation_id='AM',
                              expected_offer_id='AFQA')


def test_put_recommendations_returns_a_specific_reco_first_if_requested_with_tuto_mediationid(app):
    subtest_recos_with_params('mediationId=AE',
                              expected_status=200,
                              expected_mediation_id='AE',
                              is_tuto=True)


def test_put_recommendations_returns_404_for_given_offer_and_mediation_but_different_event():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL + '?offerId=AQ&mediationId=AE', json={})

    # then
    assert response.status_code == 404


def test_put_recommendations_returns_404_for_unknown_offer_and_known_mediation():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL + '?offerId=ABCDE&mediationId=AM', json={})

    # then
    assert response.status_code == 404


def test_put_recommendations_returns_404_for_known_offer_and_unknown_mediation():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL + '?offerId=AE&mediationId=ABCDE', json={})

    # then
    assert response.status_code == 404


def test_put_recommendations_returns_404_for_unknown_offer_and_unknown_mediation():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL + '?offerId=ABCDE&mediationId=ABCDE', json={})

    # then
    assert response.status_code == 404


# def test_15_if_i_request_a_specific_reco_with_single_reco_it_should_be_single():
#    r = req_with_auth().put(RECOMMENDATION_URL+'?offerType=event&offerId=AE&singleReco=true', json={})
#    assert r.status_code == 200
#    recos = r.json()
#    assert len(recos) == 1
#    assert recos[0]['mediation']['eventId'] == 'AE'


def test_put_recommendations_returns_no_tutos_once_they_are_marked_as_read():
    # given
    response = req_with_auth().put(RECOMMENDATION_URL, json={})
    recos_before = response.json()
    assert recos_before[0]['mediation']['tutoIndex'] == 0
    assert recos_before[1]['mediation']['tutoIndex'] == 1
    payload = {'dateRead': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}

    # when
    response_patch = req_with_auth().patch(API_URL + '/recommendations/' + recos_before[0]['id'], json=payload)

    # then
    assert response_patch.status_code == 200
    response = req_with_auth().put(RECOMMENDATION_URL, json={})
    recos_after = response.json()
    assert recos_after[0]['mediation']['tutoIndex'] == 1
    assert 'mediation' not in recos_after[1] or recos_after[1]['mediation']['tutoIndex'] is None


def test_put_recommendations_does_not_return_already_seen_recos():
    # given
    response = req_with_auth().put(RECOMMENDATION_URL, json={})
    seen_recommendations_ids = list(map(lambda x: x['id'], response.json()[:20]))

    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': seen_recommendations_ids})

    # then
    recommended_ids = [reco['id'] for reco in (response.json())]
    intersection_between_seen_and_recommended = set(seen_recommendations_ids).intersection(set(recommended_ids))
    assert not intersection_between_seen_and_recommended


def test_patch_recommendations_returns_is_clicked_true():
    # given
    response = req_with_auth().put(RECOMMENDATION_URL, json={})
    reco_id = response.json()[0]['id']

    # when
    r_update = req_with_auth().patch(API_URL + '/recommendations/' + reco_id, json={'isClicked': True})

    # then
    assert r_update.status_code == 200
    assert r_update.json()['isClicked']

@clean_database
@pytest.mark.standalone
def test_put_recommendation_does_not_return_soft_deleted_recommendation(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user(email='test@email.com', password='P@55w0rd')
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(offerer, event_occurrence1)
    stock2 = create_stock_from_event_occurrence(offerer, event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(offerer, thing_offer1)
    stock4 = create_stock_from_offer(offerer, thing_offer2)
    stock1.isSoftDeleted = True
    stock3.isSoftDeleted = True
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


def test_get_recommendations_returns_one_recommendation_found_from_search():
    # get
    response = req_with_auth().get(RECOMMENDATION_URL + '?search=Training', json={})
    recommendations = response.json()

    # then
    assert 'Training' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'Training'

    # get
    response = req_with_auth().get(RECOMMENDATION_URL + '?search=Rencontre', json={})
    recommendations = response.json()

    # then
    assert 'sur la route des migrants ; rencontres à Calais' in recommendations[0]['offer']['eventOrThing']['name']
    assert recommendations[0]['search'] == 'Rencontre'
