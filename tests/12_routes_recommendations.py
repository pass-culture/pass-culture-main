""" recommendations """
from collections import Counter

from utils.config import BLOB_SIZE
from utils.test_utils import API_URL, req, req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


def test_10_put_recommendations_should_work_only_when_logged_in():
    r = req.put(RECOMMENDATION_URL)
    assert r.status_code == 401


def test_11_put_recommendations_should_return_a_list_of_recommendations():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recommendations = r.json()
    assert len(recommendations) <= BLOB_SIZE
    assert recommendations[0]['mediation']['tutoIndex'] == 0
    assert recommendations[1]['mediation']['tutoIndex'] == 1
    assert len(list(filter(
        lambda reco:
        'mediation' in reco and reco['mediation']['tutoIndex'] is not None,
        recommendations
    ))) == 2
    assert len(list(filter(lambda reco: reco['isFirst'], recommendations))) == 1
    # ensure we have no duplicates
    ids = list(map(lambda reco: reco['id'], recommendations))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0


def test_12_put_recommendations_should_return_more_recommendations():
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
