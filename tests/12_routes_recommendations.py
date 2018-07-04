""" recommendations """
from collections import Counter
from datetime import datetime
from dateutil.parser import parse as parse_date

from utils.config import BLOB_SIZE
from utils.human_ids import dehumanize
from utils.test_utils import API_URL, req, req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


def test_10_put_recommendations_should_work_only_when_logged_in():
    r = req.put(RECOMMENDATION_URL)
    assert r.status_code == 401


def check_recos(recos):
    # ensure we have no duplicate mediations
    ids = list(filter(lambda id: id != None,
                      map(lambda reco: reco['mediationId'],
                          recos)))
    assert len(list(filter(lambda v: v>1, Counter(ids).values()))) == 0

    # ensure we have no mediations for which all offers are past their bookingLimitDatetime
    for reco in recos:
        if 'mediation' in reco\
           and 'tutoIndex' not in reco['mediation']:
            assert not all([offer['bookingLimitDatetime'] is not None and
                            parse_date(offer['bookingLimitDatetime']) <= datetime.utcnow()
                            for offer in oc['offers'] for oc in reco['mediatedOccurences']])
            if not reco['event']['isNational']:
                assert not all([oc['venue']['departementCode'] != '93' for oc in reco['mediatedOccurences']])


def subtest_initial_recos():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos = r.json()
    assert len(recos) == BLOB_SIZE + 2

    assert recos[0]['mediation']['tutoIndex'] == 0
    assert recos[1]['mediation']['tutoIndex'] == 1

    assert len(list(filter(lambda reco: 'mediation' in reco and
                                        reco['mediation']['tutoIndex'] is not None,
                           recos))) == 2


    check_recos(recos)
    return recos


def subtest_recos_with_params(params,
                              expected_status=200,
                              expected_mediation_id=None,
                              expected_occasion_type=None,
                              expected_occasion_id=None):
    r = req_with_auth().put(RECOMMENDATION_URL+'?'+params, json={})
    assert r.status_code == expected_status
    if expected_status == 200:
        recos = r.json()
        assert len(recos) <= BLOB_SIZE + (2 if expected_mediation_id is None
                                            else 3)
        assert recos[1]['mediation']['tutoIndex'] is not None
        check_recos(recos)
        return recos


def test_11_put_recommendations_should_return_a_list_of_recos():
    recos1 = subtest_initial_recos()
    assert len(list(filter(lambda reco: 'mediation' in reco and
                                        'event' in reco['mediation'] and
                                        reco['mediation']['event'] is not None,
                           recos1))) > 0
    recos2 = subtest_initial_recos()
    assert len(recos1) == len(recos2)
    assert any([recos1[i]['id'] != recos2[i]['id']
                for i in range(2, len(recos1))])


def test_12_if_i_request_a_specific_reco_it_should_be_first():
    # Full request
    subtest_recos_with_params('occasionType=event&occasionId=AE&mediationId=AM',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AM'),
                              expected_occasion_type='event',
                              expected_occasion_id=dehumanize('AE'))
    # No mediationId but occasionId
    subtest_recos_with_params('occasionType=event&occasionId=AE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AM'),
                              expected_occasion_type='event',
                              expected_occasion_id=dehumanize('AE'))
    # No occasionId but mediationId and occasionType
    subtest_recos_with_params('occasionType=event&mediationId=AE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AM'),
                              expected_occasion_type='event',
                              expected_occasion_id=dehumanize('AE'))
    # No occasionId, no occasionType, but mediationId
    subtest_recos_with_params('mediationId=AE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AM'),
                              expected_occasion_type='event',
                              expected_occasion_id=dehumanize('AE'))
    # no occasionType but mediationId and occasionId
    subtest_recos_with_params('occasionId=AE&mediationId=AM',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AM'),
                              expected_occasion_type='event',
                              expected_occasion_id=dehumanize('AE'))


def test_13_requesting_a_reco_with_bad_params_should_return_reponse_anyway():
    # occasionId correct and mediationId correct but not the same event
    subtest_recos_with_params('occasionType=event&occasionId=AQ&mediationId=AE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AE')) # FIRST TUTO MEDIATION
    # occasionId correct and mediationId correct but not the same occasion type
    subtest_recos_with_params('occasionType=event&occasionId=A9&mediationId=AM',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AE'))
    # invalid (not matching an object) occasionId with valid mediationId
    subtest_recos_with_params('occasionType=event&occasionId=ABCDE&mediationId=AM',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AE'))
    # invalid (not matching an object) mediationId with valid occasionId
    subtest_recos_with_params('occasionType=event&occasionId=AE&mediationId=ABCDE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AE'))
    # invalid (not matching an object) mediationId with invalid (not matching an object) occasionId
    subtest_recos_with_params('occasionType=event&occasionId=ABCDE&mediationId=ABCDE',
                              expected_status=200,
                              expected_mediation_id=dehumanize('AE'))


def test_14_actual_errors_should_generate_a_400():
    # wrong occasionType with valid occasionId
    subtest_recos_with_params('occasionType=invalid&occasionId=AE',
                              expected_status=400)
    #TODO
    # invalid (not dehumanizable) occasionId with valid mediationId
    # subtest_recos_with_params('occasionType=event&occasionId=00&mediationId=AE',
    #                          expected_status=400)
    # invalid (not dehumanizable) mediationId with valid occasionId
    #subtest_recos_with_params('occasionType=event&occasionId=AE&mediationId=00',
    #                          expected_status=400)
    # invalid (not dehumanizable) mediationId with invalid (not dehumanizable) occasionId
    #subtest_recos_with_params('occasionType=event&occasionId=00&mediationId=00',
    #                          expected_status=400)


def test_16_once_marked_as_read_tutos_should_not_come_back():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos_before = r.json()
    assert recos_before[0]['mediation']['tutoIndex'] == 0
    assert recos_before[1]['mediation']['tutoIndex'] == 1
    r_update = req_with_auth().patch(API_URL + '/recommendations/' + recos_before[0]['id'],
                                     json={'dateRead': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')})
    assert r_update.status_code == 200

    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos_after = r.json()
    assert recos_after[0]['mediation']['tutoIndex'] == 1
    assert 'mediation' not in recos_after[1]\
           or recos_after[1]['mediation']['tutoIndex'] is None


def test_17_put_recommendations_should_return_more_recos():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos = r.json()
    # ensure we still have no duplicates
    ids = list(map(lambda reco: reco['id'], recos))
    assert len(list(filter(lambda v: v > 1, Counter(ids).values()))) == 0


def test_18_patch_recommendations_should_return_is_clicked_true():
    r = req_with_auth().put(RECOMMENDATION_URL, json={})
    assert r.status_code == 200
    recos = r.json()
    recoId = recos[0]['id']
    r_update = req_with_auth().patch(API_URL + '/recommendations/' + recoId,
                                     json={'isClicked': True})
    assert r_update.status_code == 200
    assert r_update.json()['isClicked']
