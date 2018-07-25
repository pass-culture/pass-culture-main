from utils.test_utils import API_URL, req_with_auth


def test_10_get_venues_should_return_a_list_of_venues():
    r = req_with_auth().get(API_URL + '/venues')
    assert r.status_code == 200
    venues = r.json()
    assert len(venues) > 0


def test_11_modify_venue():
    r_before = req_with_auth().get(API_URL + '/venues/AE')
    assert r_before.status_code == 200
    r_mod = req_with_auth().patch(API_URL + '/venues/AE',
                                  json={'name': 'Ma librairie'})
    print("ERROR", r_mod.json())
    assert r_mod.status_code == 200
    r_after = req_with_auth().get(API_URL + '/venues/AE')
    assert r_after.status_code == 200
    assert r_after.json()['name'] == 'Ma librairie'

#TODO: check venue modification with missing items

def test_12_modify_venue_bad_siret():
    r_mod = req_with_auth().patch(API_URL + '/venues/AE',
                                  json={'siret': '999'})
    assert r_mod.status_code == 400
    assert 'siret' in r_mod.json()
    r_mod = req_with_auth().patch(API_URL + '/venues/AE',
                                  json={'siret': '12345678901234'})
    assert r_mod.status_code == 400
    assert 'siret' in r_mod.json()


def test_13_create_venue():
    venue_data = {'name': 'Ma venue',
                  'siret': '30255917810045',
                  'address': '75 Rue Charles Fourier, 75013 Paris',
                  'postalCode': '75200',
                  'bookingEmail': 'toto@btmx.fr',
                  'city': 'Paris',
                  'managingOffererId': 'AE',
                  'latitude': 48.82387,
                  'longitude': 2.35284
                 }
    r_create = req_with_auth().post(API_URL + '/venues/',
                                    json=venue_data)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/venues/'+id)
    assert r_check.status_code == 200
    created_venue_data = r_check.json()
    for (key, value) in venue_data.items():
        assert created_venue_data[key] == venue_data[key]
    #TODO: check thumb presence
    #TODO: check offerer linked to venue at creation