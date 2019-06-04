from models.pc_object import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user, create_offerer, create_venue, \
    create_stock_with_event_offer
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # given
            user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            PcObject.save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request = TestClient().with_auth('test@email.com') \
                .get(API_URL + '/stocks/' + humanized_stock_id)
            # then
            assert request.status_code == 200
            assert request.json()['available'] == 10
            assert request.json()['price'] == 10

    class Returns404:
        @clean_database
        def when_stock_is_soft_deleted(self, app):
            # given
            user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10, is_soft_deleted=True)
            PcObject.save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request = TestClient().with_auth('test@email.com') \
                .get(API_URL + '/stocks/' + humanized_stock_id)

            # then
            assert request.status_code == 404