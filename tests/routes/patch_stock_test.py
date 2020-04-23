from datetime import timedelta
from unittest.mock import patch

from models import Stock, Provider
from repository import repository
from repository.provider_queries import get_provider_by_local_class
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
            stock = create_stock_with_event_offer(offerer, venue, price=10, quantity=10)
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'quantity': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['quantity'] == 5
            assert request_after_update.json['price'] == 20

        @clean_database
        def when_user_is_admin(self, app):
            # given
            user = create_user(can_book_free_offers=False, email='test@email.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, quantity=10)
            repository.save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'quantity': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['quantity'] == 5
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

        @patch('routes.stocks.feature_queries.is_active', return_value=True)
        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_stock_is_edited_expect_offer_id_to_be_added_to_redis(self, mock_redis, mock_feature, app):
            # given
            beneficiary = create_user()
            offerer = create_offerer()
            create_user_offerer(beneficiary, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, quantity=10)
            repository.save(stock)

            # when
            request_update = TestClient(app.test_client()).with_auth(beneficiary.email) \
                .patch('/stocks/' + humanize(stock.id), json={'quantity': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

        @clean_database
        def when_offer_come_from_allocine_provider_and_fields_updated_in_stock_are_editable(self, app):
            # given
            allocine_provider = get_provider_by_local_class('AllocineStocks')
            pro = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id,
                                                    id_at_providers='allo')
            stock = create_stock(quantity=10, id_at_providers='allo-cine', offer=offer)

            repository.save(pro, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth(pro.email) \
                .patch(f'/stocks/{humanized_stock_id}', json={'quantity': 5, 'price': 20})

            # then
            assert request_update.status_code == 200

            updated_stock = Stock.query.one()
            assert updated_stock.quantity == 5
            assert updated_stock.price == 20

        @patch('routes.stocks.have_beginning_date_been_modified')
        @patch('routes.stocks.send_batch_stock_postponement_emails_to_users')
        @patch('routes.stocks.send_raw_email')
        @patch('routes.stocks.find_not_cancelled_bookings_by_stock')
        @clean_database
        def when_stock_changes_date_and_should_send_email_to_users(self,
                                                                   find_not_cancelled_bookings_by_stock,
                                                                   email_function,
                                                                   mocked_send_batch_stock_postponement_emails_to_users,
                                                                   mocked_check_have_beginning_date_been_modified,
                                                                   app):
            # Given
            user = create_user()
            admin = create_user(can_book_free_offers=False, email='admin@example.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            booking_cancelled = create_booking(user=user, stock=stock, venue=venue, is_cancelled=True)
            booking_used = create_booking(user=user, stock=stock, venue=venue, is_used=True)
            repository.save(booking, booking_used, booking_cancelled, admin)
            mocked_check_have_beginning_date_been_modified.return_value = True
            find_not_cancelled_bookings_by_stock.return_value = [booking, booking_used]
            serialized_date = serialize(stock.beginningDatetime + timedelta(days=1))

            # When
            request_update = TestClient(app.test_client()).with_auth(admin.email) \
                .patch('/stocks/' + humanize(stock.id), json={'beginningDatetime': serialized_date})

            # Then
            assert request_update.status_code == 200
            mocked_check_have_beginning_date_been_modified.assert_called_once()
            mocked_send_batch_stock_postponement_emails_to_users.assert_called_once_with([booking, booking_used],
                                                                                         email_function)

        @patch('routes.stocks.have_beginning_date_been_modified')
        @patch('routes.stocks.send_batch_stock_postponement_emails_to_users')
        @clean_database
        def when_stock_date_has_not_been_changed_and_should_not_email_to_beneficiaries(self,
                                                                                       mocked_send_batch_stock_postponement_emails_to_users,
                                                                                       mocked_have_beginning_date_been_modified,
                                                                                       app):
            # Given
            user = create_user()
            admin = create_user(can_book_free_offers=False, email='admin@example.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock)
            repository.save(booking, admin)
            mocked_have_beginning_date_been_modified.return_value = False

            # When
            request_update = TestClient(app.test_client()).with_auth(admin.email) \
                .patch('/stocks/' + humanize(stock.id), json={'price': 20})

            # Then
            assert request_update.status_code == 200
            mocked_have_beginning_date_been_modified.assert_called_once()
            mocked_send_batch_stock_postponement_emails_to_users.assert_not_called()

    class Returns400:
        @clean_database
        def when_wrong_type_for_quantity(self, app):
            # given
            user = create_user()
            user_admin = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, quantity=1)
            booking = create_booking(user=user, stock=stock, venue=venue, recommendation=None)
            repository.save(booking, user_admin)

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'quantity': ' '})

            # then
            assert response.status_code == 400
            assert response.json['quantity'] == ['Saisissez un nombre valide']

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
        def when_quantity_below_existing_bookings_quantity(self, app):
            # given
            user = create_user()
            user_admin = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, quantity=1)
            booking = create_booking(user=user, stock=stock, venue=venue, recommendation=None)
            repository.save(booking, user_admin)

            # when
            response = TestClient(app.test_client()).with_auth('email@test.com') \
                .patch('/stocks/' + humanize(stock.id), json={'quantity': 0})

            # then
            assert response.status_code == 400
            assert response.json['quantity'] == [
                'Le stock total ne peut être inférieur au nombre de réservations'
            ]

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
            offer = create_offer_with_thing_product(venue, last_provider_id=tite_live_provider.id,
                                                    last_provider=tite_live_provider)
            stock = create_stock(quantity=10, offer=offer)
            repository.save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth('test@email.com') \
                .patch('/stocks/' + humanized_stock_id, json={'quantity': 5})

            # then
            assert request_update.status_code == 400
            request_after_update = TestClient(app.test_client()).with_auth('test@email.com').get(
                '/stocks/' + humanized_stock_id)
            assert request_after_update.json['quantity'] == 10
            assert request_update.json["global"] == ["Les offres importées ne sont pas modifiables"]

        @clean_database
        def when_update_allocine_offer_with_new_values_for_non_editable_fields(self, app):
            # given
            allocine_provider = get_provider_by_local_class('AllocineStocks')
            pro = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id,
                                                    id_at_providers='test')
            stock = create_stock(quantity=10, id_at_providers='test-test', offer=offer)
            repository.save(pro, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient(app.test_client()).with_auth(pro.email) \
                .patch(f'/stocks/{humanized_stock_id}',
                       json={'quantity': 5, 'price': 20, 'beginningDatetime': '2020-02-08T14:30:00Z'})

            # then
            assert request_update.status_code == 400
            assert request_update.json['global'] == [
                'Pour les offres importées, certains champs ne sont pas modifiables']

            existing_stock = Stock.query.one()
            assert existing_stock.quantity == 10

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
                .patch('/stocks/' + humanize(stock.id), json={'quantity': 5})

            # then
            assert response.status_code == 403
            assert "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information." in response.json[
                'global']
