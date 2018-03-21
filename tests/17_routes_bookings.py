from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth


def test_10_create_booking():
    booking_json = {
        'offerId': humanize(3),
        'userMediationId': humanize(1)
    }
    r_create = req_with_auth().post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/'+id)
    assert r_check.status_code == 200
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]
