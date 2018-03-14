from utils.config import BLOB_LIMIT
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth

UM_URL = API_URL + '/userMediations'


def test_10_put_user_mediations_should_work_only_when_logged_in():
    r = req.put(UM_URL)
    assert r.status_code == 401


def test_11_put_user_mediations_should_return_a_list_of_ums():
    r = req_with_auth().put(UM_URL+'?around='+humanize(10), json={})
    assert r.status_code == 200
    ums = r.json()
    assert len(ums) >= BLOB_LIMIT
