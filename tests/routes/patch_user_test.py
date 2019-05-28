import pytest

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user
from utils.human_ids import humanize


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_changes_are_allowed(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            data = {'publicName': 'plop', 'email': 'new@email.com', 'postalCode': '93020', 'phoneNumber': '0612345678',
                    'departementCode': '97'}

            # when
            response = TestClient().with_auth(email=user.email) \
                .patch(API_URL + '/users/current', json=data)

            # then
            db.session.refresh(user)
            assert response.status_code == 200
            assert response.json()['id'] == humanize(user.id)
            assert response.json()['publicName'] == user.publicName
            assert user.publicName == data['publicName']
            assert response.json()['email'] == user.email
            assert user.email == data['email']
            assert response.json()['postalCode'] == user.postalCode
            assert user.postalCode == data['postalCode']
            assert response.json()['phoneNumber'] == user.phoneNumber
            assert user.phoneNumber == data['phoneNumber']
            assert response.json()['departementCode'] == user.departementCode
            assert user.departementCode == data['departementCode']
            assert 'expenses' in response.json()

    class Returns400:
        @clean_database
        def when_changes_are_forbidden(self, app):
            # given
            user = create_user(can_book_free_offers=True, is_admin=False)
            PcObject.save(user)

            data = {'isAdmin': True, 'canBookFreeOffers': False, 'firstName': 'Jean', 'lastName': 'Martin',
                    'dateCreated': '2018-08-01 12:00:00', 'resetPasswordToken': 'abc',
                    'resetPasswordTokenValidityLimit': '2020-07-01 12:00:00'}

            # when
            response = TestClient().with_auth(email=user.email) \
                .patch(API_URL + '/users/current', json=data)

            # then
            db.session.refresh(user)
            assert response.status_code == 400
            for key in data:
                assert response.json()[key] == ['Vous ne pouvez pas changer cette information']
