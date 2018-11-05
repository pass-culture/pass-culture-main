""" recommendations """
from collections import Counter
from datetime import datetime

from dateutil.parser import parse as parse_date

from utils.config import BLOB_SIZE
from utils.test_utils import API_URL, req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


def assert_no_duplicate_mediations(recos):
    mediation_ids = map(lambda recommendation: recommendation['mediationId'], recos)
    ids = list(filter(lambda mediation_id: mediation_id is not None, mediation_ids))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0


def assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos):
    recos_without_tutos = _remove_tutos(recos)
    for reco in recos_without_tutos:
        if not reco['offer']['eventOrThing']['isNational'] :
            assert reco['offer']['venue']['departementCode'] == '93'


def _remove_tutos(recos):
    return [r for r in recos if 'mediation' not in r or 'tutoIndex' not in r['mediation']]


def assert_no_mediations_with_stock_past_their_booking_limit(recos):
    recos_without_tutos = _remove_tutos(recos)
    for reco in recos_without_tutos:
        assert not all([
            stock['bookingLimitDatetime'] is not None
            and parse_date(stock['bookingLimitDatetime']) <= datetime.utcnow()
            for stock in reco['offer']['stocks']]
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


def test_put_recommendations_returns_a_list_of_recos_starting_with_two_tutos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert recos[0]['mediation']['tutoIndex'] == 0
    assert recos[1]['mediation']['tutoIndex'] == 1
    recos_with_tutos = filter(lambda reco: 'mediation' in reco and reco['mediation']['tutoIndex'] is not None, recos)
    assert len(list(recos_with_tutos)) == 2


<<<<<<< HEAD
=======
def test_put_recommendations_returns_a_list_of_a_certain_number_of_recos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert response.status_code == 200
    assert len(recos) == 82


>>>>>>> changed assertion reco
def test_put_recommendations_returns_no_duplicate_mediations_in_recos():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert_no_duplicate_mediations(recos)


def test_put_recommendations_returns_no_recos_with_mediations_with_stock_past_their_booking_limit():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert_no_mediations_with_stock_past_their_booking_limit(recos)


def test_put_recommendations_returns_recos_with_venues_in_93_if_event_is_not_national():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert_recos_offer_venue_is_in_93_is_event_is_not_national(recos)


def test_put_recommendations_returns_at_least_one_reco_with_mediation_and_offer():
    # when
    response = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos = response.json()
    assert len(list(filter(lambda reco: 'mediationId' in reco and 'offerId' in reco, recos))) > 0


def test_put_recommendations_returns_same_quantity_of_recommendations_in_different_orders():
    # given
    response1 = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})
    recos1 = response1.json()

    # when
    response2 = req_with_auth().put(RECOMMENDATION_URL, json={'seenRecommendationIds': []})

    # then
    recos2 = response2.json()
    assert len(recos1) == len(recos2)
    assert any([recos1[i]['id'] != recos2[i]['id'] for i in range(2, len(recos1))])


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
