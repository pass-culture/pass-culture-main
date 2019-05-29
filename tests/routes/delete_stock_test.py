import pytest

from models import Booking
from models.pc_object import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_booking, create_user, create_user_offerer, create_offerer, create_venue, \
    create_stock_with_event_offer
from utils.human_ids import humanize


@pytest.mark.standalone
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
            PcObject.save(user, stock, user_offerer)

            # when
            response = TestClient().with_auth('test@email.com') \
                .delete(API_URL + '/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 200
            assert response.json()['isSoftDeleted'] is True

        @clean_database
        def when_bookings_exist_on_stock(self, app):
            # given
            user = create_user(email='test@email.com')
            other_user = create_user(email='consumer@test.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking1 = create_booking(other_user, stock=stock, is_cancelled=False)
            booking2 = create_booking(other_user, stock=stock, is_cancelled=False)
            PcObject.save(user, stock, user_offerer, booking1, booking2)

            # when
            TestClient().with_auth('test@email.com') \
                .delete(API_URL + '/stocks/' + humanize(stock.id))

            # then
            bookings = Booking.query.filter_by(isCancelled=True).all()
            assert booking1 in bookings
            assert booking2 in bookings

    class Returns403:
        @clean_database
        def when_current_user_has_no_rights_on_offer(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.save(user, stock)

            # when
            response = TestClient().with_auth('test@email.com') \
                .delete(API_URL + '/stocks/' + humanize(stock.id))

            # then
            assert response.status_code == 403
