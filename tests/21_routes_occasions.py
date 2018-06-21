from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, req, req_with_auth


def test_10_get_occasions_should_return_a_list_of_occasions():
    r = req_with_auth().get(API_URL + '/occasions')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 10
    last_id = dehumanize(occasions[0]['id'])
    r = req_with_auth().get(API_URL + '/occasions?page=1')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 10
    assert dehumanize(occasions[0]['id']) == last_id
    r = req_with_auth().get(API_URL + '/occasions?page=2')
    assert r.status_code == 200
    occasions2 = r.json()
    assert dehumanize(occasions2[0]['id']) == last_id-10
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(1))
    assert r.status_code == 200
    occasions2 = r.json()
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(2))
    assert r.status_code == 200
    occasions2 = r.json()


def test_11_create_thing_occasion():
    data = {
            'venueId': humanize(3),
            'thingId': humanize(1)
           }
    r_create = req_with_auth().post(API_URL + '/occasions', json=data)
    assert r_create.status_code == 201


def test_12_create_event_occasion():
    data = {
            'venueId': humanize(3),
            'eventId': humanize(1)
           }
    r_create = req_with_auth().post(API_URL + '/occasions', json=data)
    assert r_create.status_code == 201
