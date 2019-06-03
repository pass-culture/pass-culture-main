import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, API_URL


@pytest.mark.standalone
class Post:
    class Returns201:
        @clean_database
        def when_creating_a_virtual_venue(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient() \
                .with_auth(user.email) \
                .post(API_URL + '/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json()['siren'] == '418166096'
            assert response.json()['name'] == 'Test Offerer'
            virtual_venues = list(filter(lambda v: v['isVirtual'],
                                         response.json()['managedVenues']))
            assert len(virtual_venues) == 1

        @clean_database
        def when_no_address_is_provided(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient() \
                .with_auth(user.email) \
                .post(API_URL + '/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json()['siren'] == '418166096'
            assert response.json()['name'] == 'Test Offerer'

        @clean_database
        def when_current_user_is_admin(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=True)
            PcObject.save(user)

            # When
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }
            response = TestClient() \
                .with_auth(user.email) \
                .post(API_URL + '/offerers', json=body)

            # then
            assert response.status_code == 201
