from utils.test_utils import API_URL, req, req_with_auth


def test_10_get_offerers_should_work_only_when_logged_in():
    r = req.get(API_URL + '/offerers')
    assert r.status_code == 401


def test_10_get_offerers_should_return_a_list_of_offerers():
    r = req_with_auth().get(API_URL + '/offerers')
    assert r.status_code == 200
    offerers = r.json()
    assert len(offerers) > 0

#r = req.get(API_URL + '/offerers', headers={'apikey': ''})
