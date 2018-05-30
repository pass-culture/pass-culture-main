""" recommendations """
from collections import Counter
from datetime import datetime

from utils.config import BLOB_SIZE
from utils.test_utils import API_URL, req, req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


def test_10_put_recommendations_should_work_only_when_logged_in():
    r = req.put(RECOMMENDATION_URL)
    assert r.status_code == 401


def check_recos(recos):
    # ensure we have no duplicates
    ids = list(map(lambda reco: reco['id'], recos))
    assert len(list(filter(lambda v: v>1, Counter(ids).values()))) == 0

    # ensure we have no offers with past datetimelimit
    for reco in recos:
        if 'mediatedOccurences' in reco:
            for oc in reco['mediatedOccurences']:
                assert not all(offer['bookingLimitDatetime'] <= datetime.now()
                               for offer in oc['offers'])
                # todo: e we have no offers with available slots left
                # todo: ensure I never see offers I have already booked... unless the booking is canceled


def test_initial_recos():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos = r.json()
    assert len(recos) <= BLOB_SIZE

    assert recos[0]['mediation']['tutoIndex'] == 0
    assert recos[1]['mediation']['tutoIndex'] == 1

    assert len(list(filter(lambda reco: 'mediation' in reco and
                                        reco['mediation']['tutoIndex'] is not None,
                           recos))) == 2
    check_recos(recos)
    return recos

def test_11_put_recommendations_should_return_a_list_of_recos():
    recos1 = test_initial_recos()
    recos2 = test_initial_recos()
    assert len(recos1) == len(recos2)
    assert range(2, len(recos1)).any(lambda i: recos1[i].id != recos2[id])

def test_12_if_i_request_a_specific_reco_it_should_be_first():
    #TODO
    pass

def test_13_requesting_a_reco_with_bad_params_should_not_crash_the_app():
    #TODO
    pass

def test_14_if_i_request_a_non_existant_reco_it_should_be_created():
    #TODO
    pass

def test_15_if_i_request_a_non_existant_reco_it_should_be_created_with_shared_by_userId():
    #TODO
    pass

def test_16_once_marked_as_read_tutos_should_not_come_back():
    #TODO
    pass

def test_17_put_recommendations_should_return_more_recos():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recommendations = r.json()
    # print(recommendations)
    # ensure we still have no duplicates
    ids = list(map(lambda reco: reco['id'], recommendations))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0

    assert len(list(filter(
        lambda reco:
        'mediatedOccurences' in reco and reco['mediatedOccurences'] is not None and
        len(reco['mediatedOccurences']) > 1,
    recommendations))) > 0

def test_13_patch_recommendations_should_return_is_clicked_true():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recommendations = r.json()
    recommendationId = recommendations[0]['id']
    r_update = req_with_auth().patch(API_URL + '/recommendations/'+ recommendationId,
                                     json={'isClicked': True})
    assert r_update.status_code == 200
    assert r_update.json()['isClicked']
