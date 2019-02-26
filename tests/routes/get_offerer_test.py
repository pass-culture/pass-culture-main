import pytest
from datetime import timedelta, datetime

from models import PcObject
from models.db import db
from models.pc_object import serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_thing_offer, \
    create_user, \
    create_user_offerer, \
    create_venue, \
    req_with_auth
from utils.human_ids import humanize


@pytest.mark.standalone
class Get:
    class Returns404:
        @clean_database
        def when_user_offerer_not_validated(self, app):
            # Given
            user = create_user(password='p@55sw0rd!')
            PcObject.check_and_save(user)
            invalid_id = 12

            # When
            response = TestClient() \
                .with_auth(user.email, user.clearTextPassword)\
                .get(API_URL + '/offerers/%s' % invalid_id)

            # then
            assert response.status_code == 404
            assert response.json()['global'] == ['La page que vous recherchez n\'existe pas']




