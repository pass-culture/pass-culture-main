from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, req_with_auth


def test_10_get_offers_are_paginated_by_chunks_of_10():
    # when
    r = req_with_auth().get(API_URL + '/offers')

    # then
    offers = r.json()
    assert r.status_code == 200
    assert len(offers) == 10


def test_10_get_offers_is_paginated_by_default_on_page_1():
    # given
    r = req_with_auth().get(API_URL + '/offers')
    offers = r.json()
    last_id = dehumanize(offers[0]['id'])

    # when
    r = req_with_auth().get(API_URL + '/offers?page=1')

    # then
    offers = r.json()
    assert r.status_code == 200
    assert dehumanize(offers[0]['id']) == last_id


def test_10_get_offers_returns_offers_sorted_by_date_created_desc():
    request_page_1 = req_with_auth().get(API_URL + '/offers?page=1')
    request_page_2 = req_with_auth().get(API_URL + '/offers?page=2')

    offers_1 = request_page_1.json()
    offers_2 = request_page_2.json()

    assert offers_1[-1]['dateCreated'] > offers_2[0]['dateCreated']


def test_10_get_offers_is_filtered_by_given_venue_id():
    r = req_with_auth().get(API_URL + '/offers?venueId=' + humanize(1))
    offers = r.json()
    assert r.status_code == 200
    for offer in offers:
        assert offer['venueId'] == humanize(1)


def test_10_get_offers_can_be_filtered_and_paginated_at_the_same_time():
    r = req_with_auth().get(API_URL + '/offers?venueId=' + humanize(2) + '&page=2')
    offers = r.json()
    assert r.status_code == 200
    for offer in offers:
        assert offer['venueId'] == humanize(2)


def test_10_get_offers_can_be_searched_and_filtered_and_paginated_at_the_same_time():
    r = req_with_auth().get(API_URL + '/offers?venueId=' + humanize(2) + '&page=1&search=guide')
    offers = r.json()
    assert r.status_code == 200
    assert len(offers) == 10
    for offer in offers:
        assert offer['venueId'] == humanize(2)
        assert 'guide' in offer['thing']['name'].lower()


def test_11_create_thing_offer():
    data = {
        'venueId': humanize(3),
        'thingId': humanize(1)
    }
    r_create = req_with_auth().post(API_URL + '/offers', json=data)
    assert r_create.status_code == 201


def test_12_create_event_offer():
    data = {
        'venueId': humanize(3),
        'eventId': humanize(1)
    }
    r_create = req_with_auth().post(API_URL + '/offers', json=data)
    assert r_create.status_code == 201
