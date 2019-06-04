from datetime import datetime, timedelta

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offer_with_thing_product, create_user, create_offerer, \
    create_venue, \
    create_stock_with_thing_offer, create_recommendation, create_deposit, create_booking


class Get:
    class Returns200:
        @clean_database
        def when_user_is_logged_in_and_has_a_deposit(self, app):
            # given
            user = create_user(public_name='Toto', departement_code='93', email='toto@btmx.fr')
            PcObject.save(user)

            # when
            response = TestClient() \
                .with_auth(email='toto@btmx.fr') \
                .get(API_URL + '/users/current')

            # then
            assert response.status_code == 200
            json = response.json()
            assert json['email'] == 'toto@btmx.fr'
            assert 'password' not in json
            assert 'clearTextPassword' not in json
            assert 'resetPasswordToken' not in json
            assert 'resetPasswordTokenValidityLimit' not in json
            assert json['wallet_is_activated'] == False

        @clean_database
        def when_user_is_logged_in_and_has_no_deposit(self, app):
            # Given
            user = create_user(public_name='Test', departement_code='93', email='wallet_test@email.com')
            PcObject.save(user)

            deposit_date = datetime.utcnow() - timedelta(minutes=2)
            deposit = create_deposit(user, deposit_date, amount=10)
            PcObject.save(deposit)

            # when
            response = TestClient().with_auth('wallet_test@email.com').get(API_URL + '/users/current')

            # Then
            assert response.json()['wallet_is_activated'] == True

        def when_user_has_booked_some_offers(self, app):
            # Given
            user = create_user(public_name='Test', departement_code='93', email='wallet_test@email.com')
            offerer = create_offerer('999199987', '2 Test adress', 'Test city', '93000', 'Test offerer')
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue=None)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=5)
            recommendation = create_recommendation(thing_offer, user)
            deposit_1_date = datetime.utcnow() - timedelta(minutes=2)
            deposit_1 = create_deposit(user, deposit_1_date, amount=10)
            deposit_2_date = datetime.utcnow() - timedelta(minutes=2)
            deposit_2 = create_deposit(user, deposit_2_date, amount=10)
            booking = create_booking(user, stock, venue, recommendation, quantity=1)

            PcObject.save(user, venue, deposit_1, deposit_2, booking)

            # when
            response = TestClient().with_auth('wallet_test@email.com').get(API_URL + '/users/current')

            # Then
            assert response.json()['wallet_balance'] == 15
            assert response.json()['expenses'] == {
                'all': {'max': 500, 'actual': 5.0},
                'physical': {'max': 200, 'actual': 5.0},
                'digital': {'max': 200, 'actual': 0}
            }

    class Returns400:
        @clean_database
        def when_header_not_in_whitelist(self, app):
            # given
            user = create_user(email='e@mail.com', can_book_free_offers=True, is_admin=False)
            PcObject.save(user)

            # when
            response = TestClient() \
                .with_auth(email='e@mail.com') \
                .get(API_URL + '/users/current', headers={'origin': 'random.header.fr'})

            # then
            assert response.status_code == 400
            assert response.json()['global'] == ['Header non autorisé']

    class Returns401:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # when
            response = TestClient().get(API_URL + '/users/current')

            # then
            assert response.status_code == 401
