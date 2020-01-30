from datetime import timedelta
from unittest.mock import patch

from models import Stock, Provider
from repository import repository
from routes.serialization import serialize
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_user_offerer
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def when_user_has_editor_rights_on_offerer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['available'] == 5
            assert request_after_update.json['price'] == 20

        @clean_database
        def when_user_is_admin(self, app):
            # given
            user = create_user(can_book_free_offers=False, email='test@email.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            repository.save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['available'] == 5
            assert request_after_update.json['price'] == 20

        @clean_database
        def when_booking_limit_datetime_is_none_for_thing(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue)
            repository.save(user, stock)
            stock_id = stock.id

            data = {
                'price': 120,
                'offerId': humanize(stock.offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .patch('/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 200
            assert Stock.query.get(stock_id).price == 120

        @clean_database
        def when_available_below_number_of_already_existing_bookings(self, app):
            # given
            user = create_user()
            user_admin = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, available=1)
            booking = create_booking(user=user, stock=stock, venue=venue, recommendation=None)
            repository.save(booking, user_admin)

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'available': 0})

            # then
            assert response.status_code == 200
            assert 'available' in response.json

        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_stock_is_edited_expect_offer_id_to_be_added_to_redis(self, mock_redis, app):
            # given
            beneficiary = create_user()
            offerer = create_offerer()
            create_user_offerer(beneficiary, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            repository.save(stock)

            # when
            request_update = TestClient(app.test_client()).with_auth(beneficiary.email) \
                .patch('/stocks/' + humanize(stock.id), json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

        @clean_database
        def when_offer_come_from_allocine_provider_and_fields_updated_in_stock_are_editable(self, app):
            # given
            allocine_provider = Provider \
                .query \
                .filter(Provider.localClass == 'AllocineStocks') \
                .first()

            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id,
                                                    id_at_providers='allo')
            stock = create_stock(offer=offer, available=10, id_at_providers='allo-cine')
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['available'] == 5
            assert request_after_update.json['price'] == 20

    class Returns400:
        @clean_database
        def when_wrong_type_for_available(self, app):
            # given
            user = create_user()
            user_admin = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, available=1)
            booking = create_booking(user=user, stock=stock, venue=venue, recommendation=None)
            repository.save(booking, user_admin)

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'available': ' '})

            # then
            assert response.status_code == 400
            assert response.json['available'] == ['Saisissez un nombre valide']

        @clean_database
        def when_booking_limit_datetime_after_beginning_datetime(self, app):
            # given
            user = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(stock, user)
            serialized_date = serialize(stock.beginningDatetime + timedelta(days=1))

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'bookingLimitDatetime': serialized_date})

            # then
            assert response.status_code == 400
            assert response.json['bookingLimitDatetime'] == [
                'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
            ]

        @clean_database
        def when_end_limit_datetime_is_none_for_event(self, app):
            # given
            user = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(stock, user)

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'endDatetime': None})

            # then
            assert response.status_code == 400
            assert response.json['endDatetime'] == ['Ce paramètre est obligatoire']

        @clean_database
        def when_booking_limit_datetime_is_none_for_event(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(user, stock)

            data = {
                'price': 0,
                'offerId': humanize(stock.offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .patch('/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 400
            assert response.json["bookingLimitDatetime"] == ['Ce paramètre est obligatoire']

        @clean_database
        def when_offer_come_from_titelive_provider(self, app):
            # given
            tite_live_provider = Provider \
                .query \
                .filter(Provider.localClass == 'TiteLiveThings') \
                .first()

            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, last_provider_id=tite_live_provider.id)
            stock = create_stock(offer=offer, available=10)
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'available': 5})

            # then
            assert request_update.status_code == 400
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['available'] == 10
            assert request_update.json["global"] == ["Les offres importées ne sont pas modifiables"]

        @clean_database
        def when_offer_come_from_allocine_provider_and_some_fields_updated_are_not_editable(self, app):
            # given
            allocine_provider = Provider \
                .query \
                .filter(Provider.localClass == 'AllocineStocks') \
                .first()

            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id,
                                                    id_at_providers='test')
            stock = create_stock(offer=offer, available=10, id_at_providers='test-test')
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id,
                       json={'available': 5, 'price': 20, 'endDatetime': '2020-02-08T14:30:00Z'})

            # then
            assert request_update.status_code == 400
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['available'] == 10
            assert request_update.json['global'] == [
                'Pour les offres importées, certains champs ne sont pas modifiables']

    class Returns403:
        @clean_database
        def when_user_has_no_rights(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(user, stock)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanize(stock.id), json={'available': 5})

            # then
            assert response.status_code == 403
            assert "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information." in response.json[
                'global']
