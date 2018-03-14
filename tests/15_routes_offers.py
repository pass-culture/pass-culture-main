from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth


def test_10_get_offers_should_return_a_list_of_offers():
    r = req_with_auth().get(API_URL + '/offers')
    assert r.status_code == 200
    offers = r.json()
    assert len(offers) > 0


def test_11_modify_offer():
    r_before = req_with_auth().get(API_URL + '/offers/EY')
    assert r_before.status_code == 200
    r_mod = req_with_auth().patch(API_URL + '/offers/EY',
                                json={'price': 1234})
    assert r_mod.status_code == 200
    r_after = req_with_auth().get(API_URL + '/offers/EY')
    assert r_after.status_code == 200
    assert r_after.json()['price'] == 1234

#TODO: check offer modification with missing items or incorrect values


def test_12_create_offer():
    offer_data = {'price': 1222,
                  'offererId': humanize(3),
                  'venueId': humanize(3),
                  'thingId': humanize(1)
                 }
    r_create = req_with_auth().post(API_URL + '/offers/',
                                  json=offer_data)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/offers/'+id)
    assert r_check.status_code == 200
    created_offer_data = r_check.json()
    for (key, value) in offer_data.items():
        assert created_offer_data[key] == offer_data[key]
    #TODO: check thumb presence


def test_13_search_offers_by_author():
    r = req_with_auth().get(API_URL + '/offers?search=Jules')
    assert r.status_code == 200
    offers = r.json()
    assert len(offers) > 0

