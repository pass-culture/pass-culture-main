import pytest
from datetime import datetime, timedelta
from pprint import pprint

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_booking, \
    create_deposit, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_user_offerer, \
    create_stock_from_offer, \
    create_venue, create_thing_offer, create_bank_information
from utils.human_ids import humanize

@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights(self, app):
            # given
                user = create_user(email='user@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)

                PcObject.check_and_save(user, user_offerer, offer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + '/offers')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "pas encore de stock"
                assert response_json[0]['bookingEmail'] == 'booking.email@test.com'
                assert response_json[0]['eventId'] is None
                assert response_json[0]['stocks'] == []
                assert response_json[0]['thing'] is not None
                assert response_json[0]['thing']['offerType'] is not None
                assert response_json[0]['venue'] is not None

