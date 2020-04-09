from datetime import timedelta, datetime
from unittest.mock import patch

from models import StockSQLEntity, Provider
from repository import repository
from routes.serialization import serialize
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import dehumanize, humanize


class Post:
    class Returns201:
        @patch('routes.mediations.feature_queries.is_active', return_value=True)
        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_user_has_rights(self, mock_add_offer_id_to_redis, mock_feature, app):
            # Given
            user = create_user(email='test@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user_offerer, offer)

            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
            repository.save(user)

            # When
            response = TestClient(app.test_client()).with_auth('test@email.fr') \
                .post('/stocks', json=stock_data)

            # Then
            assert response.status_code == 201
            id = response.json['id']

            stock = StockSQLEntity.query.filter_by(id=dehumanize(id)).first()
            assert stock.price == 1222

        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_booking_limit_datetime_is_none_for_thing(self, mock_add_offer_id_to_redis, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 201
            assert response.json["price"] == 0
            assert response.json["bookingLimitDatetime"] is None

            id = response.json['id']
            stock = StockSQLEntity.query.filter_by(id=dehumanize(id)).first()
            assert stock.price == 0
            assert stock.bookingLimitDatetime is None

        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_stock_is_created_expect_offer_id_to_be_added_to_redis(self, mock_add_offer_id_to_redis, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(offer)
            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}

            # When
            TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/stocks', json=stock_data)

            # Then
            mock_add_offer_id_to_redis.assert_called()
            mock_args, mock_kwargs = mock_add_offer_id_to_redis.call_args
            assert mock_kwargs['offer_id'] == offer.id

    class Returns400:
        @clean_database
        def when_missing_offer_id(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user, offer)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json={'price': 1222})

            # Then
            assert response.status_code == 400
            assert response.json["offerId"] == ['Ce paramètre est obligatoire']

        @clean_database
        def when_booking_limit_datetime_after_beginning_datetime(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='email@test.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            repository.save(user, offer)

            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 1222,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'bookingLimitDatetime': serialize(beginningDatetime + timedelta(days=2))
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 400
            assert response.json['bookingLimitDatetime'] == [
                'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
            ]

        @clean_database
        def when_invalid_format_for_booking_limit_datetime(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': 'zbbopbjeo'
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 400
            assert response.json["bookingLimitDatetime"] == ["Format de date invalide"]

        @clean_database
        def when_booking_limit_datetime_is_none_for_event(self, app):
            # Given
            beginningDatetime = datetime(2019, 2, 14)
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            repository.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None,
                'beginningDatetime': serialize(beginningDatetime),
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 400
            assert response.json["bookingLimitDatetime"] == ['Ce paramètre est obligatoire']

        @clean_database
        def when_setting_beginning_datetime_on_offer_with_thing(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='test@email.fr', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user, offer)
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'bookingLimitDatetime': serialize(beginningDatetime - timedelta(days=2))
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == [
                "Impossible de mettre une date de début si l'offre ne porte pas sur un événement"
            ]

        @clean_database
        def when_stock_is_on_offer_coming_from_provider(self, app):
            # given
            tite_live_provider = Provider \
                .query \
                .filter(Provider.localClass == 'TiteLiveThings') \
                .first()

            user = create_user(email='test@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, last_provider_id=tite_live_provider.id, last_provider=tite_live_provider)
            repository.save(user_offerer, offer)

            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
            repository.save(user)

            # When
            response = TestClient(app.test_client()).with_auth('test@email.fr') \
                .post('/stocks', json=stock_data)

            # Then
            assert response.status_code == 400
            assert response.json["global"] == ["Les offres importées ne sont pas modifiables"]

    class Returns403:
        @clean_database
        def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app):
            # Given
            user = create_user(email='test@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user, offer)

            data = {'price': 1222, 'offerId': humanize(offer.id)}

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .post('/stocks', json=data)

            # Then
            assert response.status_code == 403
            assert response.json["global"] == [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
