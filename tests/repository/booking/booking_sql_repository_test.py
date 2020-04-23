from conftest import clean_database
from model_creators.generic_creators import create_user, create_offerer, create_venue, create_booking
from model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer
from models import ThingType
from repository import repository
from repository.booking.booking_sql_repository import BookingSQLRepository


class BookingSQLRepositoryTest:
    def setup_method(self):
        self.booking_sql_repository = BookingSQLRepository()

    @clean_database
    def test_returns_a_list_of_not_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        booking_sql_entity1 = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue_online)
        booking_sql_entity2 = create_booking(user=user, is_used=True, stock=book_stock, venue=venue_online)
        booking_sql_entity3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(booking_sql_entity1, booking_sql_entity2, booking_sql_entity3)

        booking1 = self.booking_sql_repository.to_domain(booking_sql_entity1)

        # when
        bookings = self.booking_sql_repository.find_active_bookings_by_user_id(user.id)

        # then
        assert len(bookings) == 2
        assert booking1 not in bookings