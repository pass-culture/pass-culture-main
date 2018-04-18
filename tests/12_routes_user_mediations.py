from collections import Counter

from utils.config import BLOB_SIZE
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth

UM_URL = API_URL + '/userMediations'


def test_10_put_user_mediations_should_work_only_when_logged_in():
    r = req.put(UM_URL)
    assert r.status_code == 401


def test_11_put_user_mediations_should_return_a_list_of_ums():
    r = req_with_auth().put(UM_URL, json={})
    assert r.status_code == 200
    ums = r.json()
    assert len(ums) <= BLOB_SIZE
    assert ums[0]['mediation']['tutoIndex'] == 0
    assert ums[1]['mediation']['tutoIndex'] == 1
    assert len(list(filter(lambda um: 'mediation' in um and
                                      um['mediation']['tutoIndex'] is not None,
                           ums))) == 2
    assert len(list(filter(lambda um: um['isFirst'], ums))) == 1
    # ensure we have no duplicates
    ids = list(map(lambda um: um['id'], ums))
    assert len(list(filter(lambda v: v>1, Counter(ids).values()))) == 0


def test_12_put_user_mediations_should_return_more_ums():
    r = req_with_auth().put(UM_URL, json={})
    assert r.status_code == 200
    ums = r.json()
    print(ums)
    # ensure we still have no duplicates
    ids = list(map(lambda um: um['id'], ums))
    assert len(list(filter(lambda v: v>1, Counter(ids).values()))) == 0

    assert len(list(filter(lambda um: 'mediatedOccurences' in um and
                                      um['mediatedOccurences'] is not None and
                                      len(um['mediatedOccurences']) > 1,
                           ums))) == 5
