from datetime import datetime, timedelta
from unittest.mock import patch

from pcapi.models import BookingSQLEntity, Provider
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
import pytest
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_user_offerer
from pcapi.model_creators.specific_creators import create_stock_with_event_offer, create_offer_with_thing_product, \
    create_offer_with_event_product
from pcapi.utils.human_ids import humanize

NOW = datetime.utcnow()


class Delete:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_current_user_has_rights_on_offer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            assert response.json['isSoftDeleted'] is True

        @pytest.mark.usefixtures("db_session")
        def expect_bookings_to_be_cancelled(self, app):
            # given
            user = create_user(email='test@email.com')
            other_user = create_user(email='consumer@test.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking1 = create_booking(other_user, is_cancelled=False, stock=stock)
            booking2 = create_booking(other_user, is_cancelled=False, stock=stock)
            repository.save(user, stock, user_offerer, booking1, booking2)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com').delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            bookings = BookingSQLEntity.query.filter_by(isCancelled=True).all()
            assert booking1 in bookings
            assert booking2 in bookings

        @pytest.mark.usefixtures("db_session")
        def when_stock_is_on_an_offer_from_allocine_provider(self, app):
            # Given
            allocine_provider = get_provider_by_local_class('AllocineStocks')
            offerer = create_offerer()
            user = create_user(email='test@email.com')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, last_provider_id=allocine_provider.id,
                                                    id_at_providers='allo')
            stock = create_stock(id_at_providers='allo-cine', offer=offer)
            repository.save(user, user_offerer, stock)

            # When
            response = TestClient(app.test_client()).with_auth(user.email) \
                .delete('/stocks/' + humanize(stock.id))

            # Then
            assert response.status_code == 200
            assert response.json['isSoftDeleted'] is True

        @patch('pcapi.routes.stocks.feature_queries.is_active', return_value=True)
        @patch('pcapi.routes.stocks.redis.add_offer_id')
        @pytest.mark.usefixtures("db_session")
        def when_stock_is_deleted_expect_offer_id_to_be_added_to_redis(self, mock_redis, mock_feature, app):
            # given
            beneficiary = create_user()
            offerer = create_offerer()
            create_user_offerer(beneficiary, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(stock)

            # when
            response = TestClient(app.test_client()).with_auth(beneficiary.email) \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_stock_is_on_an_offer_from_titelive_provider(self, app):
            # given
            tite_live_provider = Provider \
                .query \
                .filter(Provider.localClass == 'TiteLiveThings') \
                .first()

            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, last_provider_id=tite_live_provider.id, last_provider=tite_live_provider)
            stock = create_stock(offer=offer)
            repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 400
            assert response.json["global"] == ["Les offres importées ne sont pas modifiables"]


        @pytest.mark.usefixtures("db_session")
        def when_stock_is_an_event_that_ended_more_than_two_days_ago(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, beginning_datetime=NOW - timedelta(days=5),
                                                  booking_limit_datetime=NOW - timedelta(days=6))
            repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 400
            assert response.json['global'] == ["L'événement s'est terminé il y a plus de deux jours, " \
                                               "la suppression est impossible."]


    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_current_user_has_no_rights_on_offer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            repository.save(user, stock)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 403
