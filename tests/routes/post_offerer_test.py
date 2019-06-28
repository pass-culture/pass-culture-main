from models import PcObject, Offerer, RightsType, UserOfferer
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, create_user_offerer, create_offerer


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
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'
            virtual_venues = list(filter(lambda v: v['isVirtual'],
                                         response.json['managedVenues']))
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
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'

        @clean_database
        def when_current_user_is_admin(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=True)
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201

        @clean_database
        def expect_the_current_user_to_be_editor_of_the_new_offerer(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            PcObject.save(user)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.UserOfferers[0].rights == RightsType.editor

        @clean_database
        def when_offerer_already_in_base_just_create_user_offerer(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789')
            PcObject.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            user_offerer = UserOfferer.query.first()
            offerer = Offerer.query.first()
            assert user_offerer is not None
            assert offerer.UserOfferers[0].rights == RightsType.editor
            assert offerer.UserOfferers[0].validationToken is not None


    class Returns400:
        @clean_database
        def when_user_offerer_already_exist(self, app):
            # Given
            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789')
            PcObject.save(user, offerer)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user_offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }
            user_offerers = UserOfferer.query.all()

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            user_offerers_after_call = UserOfferer.query.all()
            assert len(user_offerers_after_call) == len(user_offerers)
            assert response.status_code == 400
