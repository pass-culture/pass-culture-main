from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, req_with_auth


def test_10_get_occasions_are_paginated_by_chunks_of_10():
    # when
    r = req_with_auth().get(API_URL + '/occasions')

    # then
    occasions = r.json()
    assert r.status_code == 200
    assert len(occasions) == 10


def test_10_get_occasions_is_paginated_by_default_on_page_1():
    # given
    r = req_with_auth().get(API_URL + '/occasions')
    occasions = r.json()
    last_id = dehumanize(occasions[0]['id'])

    # when
    r = req_with_auth().get(API_URL + '/occasions?page=1')

    # then
    occasions = r.json()
    assert r.status_code == 200
    assert dehumanize(occasions[0]['id']) == last_id


def test_10_get_occasions_returns_occasions_sorted_by_date_created_desc():
    request_page_1 = req_with_auth().get(API_URL + '/occasions?page=1')
    request_page_2 = req_with_auth().get(API_URL + '/occasions?page=2')

    occasions_1 = request_page_1.json()
    occasions_2 = request_page_2.json()

    assert occasions_1[-1]['dateCreated'] > occasions_2[0]['dateCreated']


def test_10_get_occasions_is_filtered_by_given_venue_id():
    r = req_with_auth().get(API_URL + '/occasions?venueId=' + humanize(1))
    occasions = r.json()
    assert r.status_code == 200
    for occasion in occasions:
        assert occasion['venueId'] == humanize(1)


def test_10_get_occasions_can_be_filtered_and_paginated_at_the_same_time():
    r = req_with_auth().get(API_URL + '/occasions?venueId=' + humanize(2) + '&page=2')
    occasions = r.json()
    assert r.status_code == 200
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)


def test_10_get_occasions_can_be_searched_and_filtered_and_paginated_at_the_same_time():
    r = req_with_auth().get(API_URL + '/occasions?venueId=' + humanize(2) + '&page=1&search=guide')
    occasions = r.json()
    assert r.status_code == 200
    assert len(occasions) == 10
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)
        assert 'guide' in occasion['thing']['name'].lower()


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
