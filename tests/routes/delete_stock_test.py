from datetime import datetime, timedelta
from unittest.mock import patch

from models import Booking, Provider
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_user_offerer
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_offer_with_thing_product
from utils.human_ids import humanize

NOW = datetime.utcnow()


class Delete:
    class Returns200:
        @clean_database
        def when_current_user_has_rights_on_offer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            Repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            assert response.json['isSoftDeleted'] is True

        @clean_database
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
            Repository.save(user, stock, user_offerer, booking1, booking2)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com').delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            bookings = Booking.query.filter_by(isCancelled=True).all()
            assert booking1 in bookings
            assert booking2 in bookings

        @patch('routes.stocks.redis.add_offer_id')
        @clean_database
        def when_stock_is_deleted_expect_offer_id_to_be_added_to_redis(self, mock_redis, app):
            # given
            beneficiary = create_user()
            offerer = create_offerer()
            create_user_offerer(beneficiary, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            Repository.save(stock)

            # when
            response = TestClient(app.test_client()).with_auth(beneficiary.email) \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    class Returns400:
        @clean_database
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
            offer = create_offer_with_thing_product(venue, last_provider_id=tite_live_provider.id)
            stock = create_stock(offer=offer)
            Repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 400
            assert response.json["global"] == ["Les offres importées ne sont pas modifiables"]


        @clean_database
        def when_stock_is_an_event_that_ended_more_than_two_days_ago(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(
                offerer, venue,
                booking_limit_datetime=NOW - timedelta(days=6),
                beginning_datetime=NOW - timedelta(days=5),
                end_datetime=NOW - timedelta(days=4)
            )
            Repository.save(user, stock, user_offerer)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 400
            assert response.json['global'] == ["L'événement s'est terminé il y a plus de deux jours, " \
                                               "la suppression est impossible."]


    class Returns403:
        @clean_database
        def when_current_user_has_no_rights_on_offer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            Repository.save(user, stock)

            # when
            response = TestClient(app.test_client()).with_auth('test@email.com') \
                .delete('/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 403
